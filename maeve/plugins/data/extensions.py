from maeve.models.core import Globals
from .backends.pandas import PandasDataFrame
from .backends.polars import PolarsDataFrame
from maeve.models.core import DataLoaderRecipe
from maeve.util import FuncUtils
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

    def unspace_colnames(self, *args, **kwargs):
        return self.backend_func("unspace_colnames", *args, **kwargs)

    def replace_column_values(self, *args, **kwargs):
        return self.backend_func("replace_column_values", *args, **kwargs)
    #########################################################
    # Do not touch
    #########################################################

    def loc_slice(self, *args, **kwargs):
        return self.backend_func("loc_slice", *args, **kwargs)

    def iloc_slice(self, *args, **kwargs):
        return self.backend_func("iloc_slice", *args, **kwargs)

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

    def __init__(self, df):
        self._df = df
        self.df_info()
        self.pandas = PandasDataFrame()
        self.polars = PolarsDataFrame()

    def mangle_columns(self):
        return self.backend_func("mangle_columns")


    def backend_func(self, func, *args, **kwargs):
        return getattr(getattr(self, self.backend), func)(self._df, *args, *kwargs)

    def df_info(self):
        self.is_pd = True if type(self._df) is pd.core.series.Series else False
        self.is_pl = True if type(self._df) is pl.series.series.Series else False

        if type(self._df) is pd.core.series.Series:
            self.backend = "pandas"
        elif type(self._df) is pl.series.series.Series:
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
        return FuncUtils.run_func(
            recipe,
            ns=backend
        )

    @staticmethod
    def get_backend(backend):
        return importlib.import_module(backend)
