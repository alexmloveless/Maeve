import pytest
from tests.global_fixtures import std_maeve_init_kwargs
from maeve import Session
import pandas as pd


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
