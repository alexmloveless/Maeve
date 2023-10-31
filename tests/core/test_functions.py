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

def test_replace_column_values(std_maeve_init_kwargs):
    # Add a column with spaces, then remove spaces
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadPandasCSVNoPipeline")
    # Update a single value with a scalar:
    df1 = df.mv.replace_column_values('streams', index=574, replace_val=0)
    assert df1.loc[574, 'streams'] == 0

    # Update a single value with value from another column, same row:
    df1 = df.mv.replace_column_values('streams', index=574, replace_cols='released_year')
    assert df1.loc[574, 'streams'] == 1970

    # Update a row with another column using query:
    df1 = df.mv.replace_column_values('streams', qry="track_name == 'Love Grows (Where My Rosemary Goes)'",
                                      replace_cols='bpm')
    assert df1.loc[574, 'streams'] == 110

    # Update a single value with value from another row, same column with a multiplier:
    df1 = df.mv.replace_column_values('streams', index=574, replace_index=575, multiplier=2)
    assert df1.loc[574, 'streams'] == '374706940374706940'

def test_clean_str_to_float(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = pd.DataFrame({'vals': ['(17.0)', '1,000.0', '-'], 'vals2': ['(27.0)', '1,025.0', '-']},
                      index=['Portland', 'Berkeley', 'Cambridge'])
    df = df.mv.apply_to_columns(Series.clean_str_to_float, ['vals', 'vals2'], fillna='0')
    assert df.vals.dtype == float
