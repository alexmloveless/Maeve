import pytest
from tests.global_fixtures import std_maeve_init_kwargs, test_data_path
from maeve import Session
import pandas as pd
from os import path


def test_pandas_load_csv(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadPandasCSVNoPipeline")
    assert type(df) is pd.core.frame.DataFrame


def test_pandas_load_parquet(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestPandasLoadParquet")
    assert type(df) is pd.core.frame.DataFrame


def test_pandas_load_csv_inline_list_pipeline(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadPandasCSVWithInlineListPipeline")
    assert "dummy" in list(df.columns)


def test_pandas_load_csv_inline_dict_pipeline(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadPandasCSVWithInlineDictPipeline")
    assert "dummy" in list(df.columns)


def test_polars_load_csv_inline_dict_pipeline(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadPorlarsCSVWithInlineDictPipeline")
    assert "dummy" in list(df.columns)


def test_pandas_pipeline_anchors_load_csv(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestPipelineDictWithAnchor")
    assert "dummy" in list(df.columns)


def test_pandas_standalone_function(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoaderPandasCSV")
    df = s.cook("TestFunctionRename", obj=df)
    assert "dummy" in list(df.columns)


def test_pandas_pipeline_no_loader(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoaderPandasCSV")
    df = s.cook("TestSimplePipelineNoLoaderPandas", obj=df)
    assert "dummy" in list(df.columns) and df.shape[0] == 175


def test_pandas_pipeline_add_catalogue_inter_named(std_maeve_init_kwargs):
    # test if catalogue_name in recipe works
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestoadPandasCSVAddToCatNamed")
    inter_df = s.c.get("TestLoadPandasCSVAddToCatNamed_Inter", method="name")
    assert "dummy" in list(inter_df.columns) and inter_df.shape[0] == 953


def test_pandas_load_csv_recipe_name_in_pipeline(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadPandasRecipeNameInPipeline")
    assert "dummy" in list(df.columns) and df.shape[0] == 175

def test_read_csv(std_maeve_init_kwargs, test_data_path):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("read_csv", path.join(test_data_path, "spotify-2023-utf-8.csv"))
    assert type(df) is pd.core.frame.DataFrame


def test_pandas_load_timeseries(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestCSVTimeSeriesTempsLoad")
    assert df.loc['1990-12-31', 'Daily minimum temperatures'] == '13'


def test_pandas_timeseries_add_data(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestTimeSeriesAddData")
    assert df.loc['1990-12-31', 'Daily minimum temperatures'] == '13'
    assert pd.isnull(df.loc['1991-01-01', 'Daily minimum temperatures'])
    assert pd.isnull(df.loc['1990-12-01', 'Daily maximum temperatures'])
    assert df.loc['1991-01-01', 'Daily maximum temperatures'] == 13.6
