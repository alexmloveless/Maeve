import maeve
from maeve.models.core import Globals
from .backends.pandas import PandasDataFrame
from .backends.pandas import PandasSeries
from .backends.polars import PolarsDataFrame
from .backends.polars import PolarsSeries
from maeve.models.core import DataLoaderRecipe, FileConcatDataLoaderRecipe
from maeve.util.function import FuncUtils
from maeve.util.os import FSUtils as fs
from maeve.plugins.plot.matplotlib import MplPlot
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
        # placeholder for the session since we won't see it until this passes through the cook function again
        # This is cos the extensions are initialised in the Dataframe creation process which isn't visible to
        # Maeve. So we stick it in later
        self.s = None

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

    def add_rows(self, *args, **kwargs):
        return self.backend_func("add_rows", *args, **kwargs)

    def del_rows_after_val(self, *args, **kwargs):
        return self.backend_func("del_rows_after_val", *args, **kwargs)

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

    def set_session(self, session, override=False):
        # if not isinstance(session, maeve.Session):
        #     return
        if (self.s and override) or not self.s:
            self.s = session
            self.pandas.set_session(session)
            self.polars.s = session

        self.plot = PandasMPLPlot(self._df, session)


class PandasMPLPlot:
    def __init__(self, df, session):
        self.s = session
        self.df = df
        # self.plot, _ = self.s.plugins.get_plugin("mpl_subplots")
        self.plot = MplPlot(session)

    def ts(self, *args, **kwargs):
        return self.plot.ts(self.df, *args, **kwargs)

@pd.api.extensions.register_series_accessor(g.core.datapackagestub)
@pl.api.register_series_namespace(g.core.datapackagestub)
class Series:

    def __init__(self, series):
        self._series = series
        self.series_info()
        self.pandas = PandasSeries()
        self.polars = PolarsSeries()
        self.s = None

    def mangle_columns(self):
        return self.backend_func("mangle_columns")

    def clean_str_to_float(self, *args, **kwargs):
        return self.backend_func("clean_str_to_float", *args, **kwargs)

    def id_to_str(self, *args, **kwargs):
        return self.backend_func("id_to_str", *args, **kwargs)

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

    def set_session(self, session, override=False):
        # if not isinstance(session, maeve.Session):
        #     return
        if (self.s and override) or not self.s:
            self.s = session
            self.pandas.s = session
            self.polars.s = session


class DataLoader:
    def __init__(self, session):
        self.s = session

    def _add_session_to_df(self, df):
        getattr(df, g.core.datapackagestub).set_session(self.s)

    def add_session(func):
        def wrapper(self, *args, **kwargs):
            ret = func(self, *args, **kwargs)
            if isinstance(ret, list):
                for df in ret:
                    self._add_session_to_df(df)
            else:
                self._add_session_to_df(ret)
            return ret
        return wrapper


    @add_session
    def load(self, recipe, obj=None):
        if obj is not None:
            return obj
        recipe = DataLoaderRecipe(**recipe).model_dump()
        backend = self.get_backend(recipe["backend"])
        return FuncUtils.run_func_recipe(
            recipe,
            ns=backend
        )

    main = load

    @add_session
    def get_files_from_recipe(self, recipe):
        return fs.os_walk_and_filter(
            recipe["location"],
            fileregex=recipe["file_regex"],
            dirregex=recipe["dir_regex"]
        )

    @add_session
    def load_files_from_recipe(self, recipe):
        files = self.get_files_from_recipe(recipe)
        dfs = []
        for f in files:
            r = DataLoaderRecipe(
                location=f,
                backend=recipe["backend"]
            )
            dfs.append(self.load(r))
        return dfs

    @add_session
    def load_files_concat(self, recipe):
        recipe = FileConcatDataLoaderRecipe(**recipe).model_dump()
        files = self.get_files_from_recipe(recipe)
        return pd.concat(files, **recipe["concat_kwargs"])

    @add_session
    def load_files_merge(self, recipe):
        pass

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
