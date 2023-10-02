import pytest
from tests.global_fixtures import std_maeve_init_kwargs
from maeve import Session
import pandas as pd


def test_load_csv(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadCSVNoPipeline")
    assert type(df) is pd.core.frame.DataFrame


def test_load_parquet(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestPandasLoadParquet")
    assert type(df) is pd.core.frame.DataFrame
