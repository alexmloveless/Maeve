from maeve.models.core import Globals
from .backends.pandas import PandasDataFrame
from .backends.pandas import PandasSeries
from .backends.polars import PolarsDataFrame
from .backends.polars import PolarsSeries
from maeve.models.core import DataLoaderRecipe
from maeve.util.function import FuncUtils
import pandas as pd
import polars as pl
import importlib

g = Globals()


@pd.api.extensions.register_dataframe_accessor(g.core.datapackagestub)
@pl.api.register_dataframe_namespace(g.core.datapackagestub)
class DataFrame:

    def __init__(self, df):
        self._df = df
        self.df_info()
        self.pandas = PandasDataFrame()
        self.polars = PolarsDataFrame()

    #########################################################
    # Functions
    #########################################################

    def myfunc(self, *args, **kwargs):
        return self.backend_func("myfunc", *args, **kwargs)

    def apply_to_columns(self, *args, **kwargs):
        return self.backend_func("apply_to_columns", *args, **kwargs)

    applyc = apply_to_columns

    def repeat(self, *args, **kwargs):
        return self.backend_func("repeat", *args, **kwargs)

    def unspace_colnames(self, *args, **kwargs):
        return self.backend_func("unspace_colnames", *args, **kwargs)

    def replace_column_values(self, *args, **kwargs):
        return self.backend_func("replace_column_values", *args, **kwargs)

    def recipe(self, df, recipe, session, **kwargs):
        return session.cook(recipe, obj=df, **kwargs)

    def loc_slice(self, *args, **kwargs):
        return self.backend_func("loc_slice", *args, **kwargs)

    def iloc_slice(self, *args, **kwargs):
        return self.backend_func("iloc_slice", *args, **kwargs)

    #########################################################
    # Do not touch
    #########################################################

    def backend_func(self, func, *args, **kwargs):
        return getattr(getattr(self, self.backend), func)(self._df, *args, **kwargs)

    def df_info(self):
        self.is_pd = True if type(self._df) is pd.core.frame.DataFrame else False
        self.is_pl = True if type(self._df) is pl.dataframe.frame.DataFrame else False

        if type(self._df) is pd.core.frame.DataFrame:
            self.backend = "pandas"
        elif type(self._df) is pl.dataframe.frame.DataFrame:
            self.backend = "polars"
        else:
            self.backend = None


@pd.api.extensions.register_series_accessor(g.core.datapackagestub)
@pl.api.register_series_namespace(g.core.datapackagestub)
class Series:

    def __init__(self, series):
        self._series = series
        self.series_info()
        self.pandas = PandasSeries()
        self.polars = PolarsSeries()

    def mangle_columns(self):
        return self.backend_func("mangle_columns")

    def clean_str_to_float(self, *args, **kwargs):
        return self.backend_func("clean_str_to_float", *args, **kwargs)

    def backend_func(self, func, *args, **kwargs):
        return getattr(getattr(self, self.backend), func)(self._series, *args, **kwargs)

    def series_info(self):
        self.is_pd = True if type(self._series) is pd.core.series.Series else False
        self.is_pl = True if type(self._series) is pl.series.series.Series else False

        if type(self._series) is pd.core.series.Series:
            self.backend = "pandas"
        elif type(self._series) is pl.series.series.Series:
            self.backend = "polars"
        else:
            self.backend = None


class DataLoader:
    def __init__(self, session):
        self.s = session

    def main(self, recipe, obj=None):
        if obj is not None:
            return obj
        recipe = DataLoaderRecipe(**recipe).model_dump()
        backend = self.get_backend(recipe["backend"])
        return FuncUtils.run_func_recipe(
            recipe,
            ns=backend
        )

    @staticmethod
    def get_backend(backend):
        return importlib.import_module(backend)


class Data:
    def __init__(self):
        pass

    def PandasDataFrame(self, *args, **kwargs):
        return pd.DataFrame(*args, **kwargs)

    DataFrame = PandasDataFrame

    def PolarsDataFrame(self, *args, **kwargs):
        return pl.DataFrame(*args, **kwargs)
