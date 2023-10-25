import pandas as pd
from pydantic import BaseModel, field_validator, conlist
from typing import Optional, Union
import re


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

    def myfunc(self, df):
        # do stuff
        return df

    def unspace_colnames(self,
                         df: pd.core.dataframe.DataFrame,
                         delim: str = "_"
                         ) -> pd.core.dataframe.DataFrame:
        """Datafunc - remove spaces from column names. Default delim is underscore.

        Parameters
        ----------
        df: Dataframe
        delim: str, default '_'
            Delimiter to replace space with
        """

        df.columns = [re.sub(" ", delim, c) for c in df.columns]
        return df

    def loc_slice(self, df, index=None, columns=None):
        mod = PandasSlicerModel(index=index, columns=columns)
        return df.loc[mod.index, mod.columns]

    def iloc_slice(self, df, index=None, columns=None):
        mod = PandasSlicerModel(index=index, columns=columns)
        return df.iloc[mod.index, mod.columns]
