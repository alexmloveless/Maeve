from maeve import Globals as g
from .backends.pandas import PandasDataFrame
from .backends.polars import PolarsDataFrame
import pandas as pd
import polars as pl

# TODO: Enable backends to be explictly enabled to minimise memory

@pd.api.extensions.register_dataframe_accessor(g.datapackagestub)
@pl.api.register_dataframe_namespace(g.datapackagestub)
class DataFrame:

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
        self.is_pd = True if type(self._df) is pd.core.frame.DataFrame else False
        self.is_pl = True if type(self._df) is pl.dataframe.frame.DataFrame else False

        if type(self._df) is pd.core.frame.DataFrame:
            self.backend = "pandas"
        elif type(self._df) is pl.dataframe.frame.DataFrame:
            self.backend = "polars"
        else:
            self.backend = None
