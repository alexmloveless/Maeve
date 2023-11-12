import pandas as pd
from pydantic import BaseModel, field_validator, conlist
from typing import Optional, Union, Any
import re

from maeve.util.function import FuncUtils


class PandasSlicerModel(BaseModel):
    index: Optional[Union[conlist(Union[int, str, None], min_length=1, max_length=3), str, int]] = None
    columns: Optional[Union[conlist(Union[int, str, None], min_length=1, max_length=3), str, int]] = None

    @field_validator('index', 'columns')
    @classmethod
    def create_slice(cls, v: Union[list, str]):
        if type(v) in [str, int]:
            v = [v]
        return slice(*v)


class PandasDataFrame:
    def __init__(self):
        pass

    @staticmethod
    def apply_to_columns(
            df: pd.DataFrame,
            func: str,
            cols: Optional[Union[str, list[str]]] = None,
            new_col: str = None,
            fail_silently: bool = False,
            *args,
            **kwargs
    ) -> pd.DataFrame:
        """Apply a series function to 1 or more columns of a dataframe.

        Parameters
        ----------
        df: pd.DataFrame
        func: object (function)
            Any function that acts on a series (can supply native pandas by pd.Series.func)
        cols: str or list of str
            The column(s) to act on
        args: arguments
            args of function being called
        new_col: str, optional, default None
            Name of the new column to be created with the new values
        fail_silently: bool, default False
            If True will log failure message and continue processing, otherwise will raise error
        args:  arguments
            args of function being called
        kwargs: keyword arguments
            kwargs of function being called

        Returns
        -------
        pd.DataFrame
        """
        cols = cols if cols else list(df.columns)
        if new_col and type(cols) is str:
            df[new_col] = FuncUtils.run_func(
                func, df[cols], fail_silently=fail_silently, func_args=args, func_kwargs=kwargs
            )
        else:
            cols = [cols] if type(cols) is str else cols
            if type(cols) is list:
                for col in cols:
                    df[col] = FuncUtils.run_func(
                        func, df[col], fail_silently=fail_silently, func_args=args, func_kwargs=kwargs
                    )
        return df

    @staticmethod
    def repeat(df: pd.DataFrame,
               func: str,
               param_list: list,
               fail_silently=False,
               ) -> pd.DataFrame:
        """Apply a function to a dataframe repeatedly using a list of parameters.

        Parameters
        ----------
        df: pd.DataFrame
        func: object (function)
            Any function that acts on a dataframe (can supply native pandas function)
        param_list: list of dicts
            Each dictionary contains arguments as keyword pairs. Each dictionary in the list will be applied to the
            dataframe.
        fail_silently: bool, default False
            If True will log failure message and continue processing, otherwise will raise error

        Returns
        -------
        pd.DataFrame
        """

        for params in param_list:
            df = FuncUtils.run_func(
                func, df, fail_silently=fail_silently, func_kwargs=params
            )
        return df

    @staticmethod
    def unspace_colnames(df: pd.DataFrame,
                         delim: str = "_"
                         ) -> pd.DataFrame:
        """Datafunc - remove spaces from column names. Default delim is underscore.

        Parameters
        ----------
        df: Dataframe
        delim: str, default '_'
            Delimiter to replace space with
        """

        df.columns = [re.sub(" ", delim, c) for c in df.columns]
        return df

    def replace_column_values(self,
                              df: pd.DataFrame,
                              change_cols: Union[str, list],
                              qry: Optional[str] = None,
                              index: Optional[Any] = None,
                              replace_val: Optional[Any] = None,
                              replace_cols: Optional[Union[str, list]] = None,
                              replace_qry: Optional[str] = None,
                              replace_index: Optional[Any] = None,
                              multiplier: Optional[float] = None,
                              aggfunc: Optional[str] = None) -> pd.DataFrame:
        """Replace values with a scalar or values from another column.

        Parameters
        ----------
        df: pd.DataFrame
        change_cols: str or list of strings
            Column name to act on
        qry: str, optional
            Query string to filter rows to be changed. Used as the replacement index if replace_qry or replace_index
            not supplied.
        index: Any, optional
            Index value or slice to filter rows to be changed.
            This or qry must be entered. If both, qry will be used.
        replace_val: Any, optional
            Scalar value to replace current values.
            Overrides remaining parameters even if they are supplied.
        replace_cols: str or list of strings, optional
            Column or list of columns whose values will be used for replacement values
        replace_qry: str, optional
            Query string to filter rows to be used for replacement values.
        replace_index: Any, optional
            Index of the row or rows to be used for replacement values
        multiplier: float, optional
            Used to multiply the new column values by
        aggfunc: str, optional
            Aggregation function to be used on the replacement values

        Returns
        -------
        pd.DataFrame

        Examples
        --------
        Update a single value with a scalar:
            replace_column_values(df, 'streams', index=574, replace_val=0)
        Update a single value with value from another column, same row:
            replace_column_values(df, 'streams', index=574, replace_cols='released_year')
        Update a number of rows with another column using query:
            replace_column_values(df, 'streams', qry="released_year == 2023", replace_cols='bpm')
        Update a single value with value from another row, same column with a multiplier:
            replace_column_values(df, 'streams', index=574, replace_index=575, multiplier=2)
        """

        if qry:
            index = df.query(qry).index
            replace_index = df.query(replace_qry).index if replace_qry else index
        elif index:
            replace_index = index if not replace_index else replace_index
        else:
            self.log.warning("Need query or index parameters.")
            return df

        replace_cols = change_cols if not replace_cols else replace_cols

        # replace_val overrides replace_index, replace_cols and multiplier even if supplied
        if replace_val is not None:
            df.loc[index, change_cols] = replace_val
        elif aggfunc is not None:
            df.loc[index, change_cols] = df.loc[replace_index, replace_cols].agg(aggfunc)
        elif replace_index != index and type(index) in [slice, tuple, list]:
            if multiplier is not None:
                df.loc[index, change_cols] = df.loc[replace_index, replace_cols].values * multiplier
            else:
                df.loc[index, change_cols] = df.loc[replace_index, replace_cols].values
        else:
            if multiplier is not None:
                df.loc[index, change_cols] = df.loc[replace_index, replace_cols] * multiplier
            else:
                df.loc[index, change_cols] = df.loc[replace_index, replace_cols]

        return df

    def loc_slice(self, df, index=None, columns=None):
        mod = PandasSlicerModel(index=index, columns=columns)
        return df.loc[mod.index, mod.columns]

    def iloc_slice(self, df, index=None, columns=None):
        mod = PandasSlicerModel(index=index, columns=columns)
        return df.iloc[mod.index, mod.columns]


class PandasSeries:
    def __init__(self):
        pass

    @staticmethod
    def clean_str_to_float(series: pd.Series,
                           fillna: str = '0') -> pd.Series:
        """Clean values from string to floats.
        Removes common non-numeric characters that can appear in Excel spreadsheets and converts to float:
            commas removed;
            '-' on its own removed (but left in if it before a number as a minus eg -1.5)
            converts brackets to a negative float;
            Positive numbers also get converted to floats.
        Eg (1,000) will become -1000.

        Parameters
        ----------
        series: pd.Series
            Data to be cleaned
        fillna: str, optional, default '0'
            Fill nans first before converting.

        Returns
        -------
        pd.Series
        """

        if fillna or type(fillna) is str:
            series = series.fillna(fillna)
        series = series.astype(str)
        series = series.str.replace(',', '')
        series = series.str.replace(r'^-$', '0', regex=True)
        series = series.apply(lambda x: -float(x.strip('()')) if '(' in x else float(x))
        return series
