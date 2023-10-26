import pytest
from tests.global_fixtures import std_maeve_init_kwargs, test_data_path
from maeve import Session
import pandas as pd
from os import path


def test_unspace_colnames(std_maeve_init_kwargs):
    # Add a column with spaces, then remove spaces
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadPandasCSVNoPipeline")
    df['new col'] = 'Y'
    df = df.mv.unspace_colnames()
    assert 'new_col' in df.columns
