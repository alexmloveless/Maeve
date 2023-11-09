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

    # Update a slice of indexes with slice from a different column:
    df1 = df.mv.replace_column_values('speechiness_%', index=slice(0, 1), replace_index=slice(2, 3),
                                      replace_cols='liveness_%')
    assert df1.loc[0, 'speechiness_%'] == 31
    assert df1.loc[1, 'speechiness_%'] == 11

    # Update a slice of indexes with slice from a different column and use an aggregation function:
    df1 = df.mv.replace_column_values('speechiness_%', index=slice(0, 1), replace_index=slice(2, 3),
                                      replace_cols='liveness_%', aggfunc='sum')
    assert df1.loc[0, 'speechiness_%'] == 42
    assert df1.loc[1, 'speechiness_%'] == 42

    # Update a range of rows using indexes list with range from a different column:
    df1 = df.mv.replace_column_values('speechiness_%', index=[2, 3], replace_index=[2, 3],
                                      replace_cols='liveness_%')
    assert df1.loc[2, 'speechiness_%'] == 31
    assert df1.loc[3, 'speechiness_%'] == 11


def test_clean_str_to_float(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    df = s.data.DataFrame({'vals': ['(17.0)', '1,000.0', '-'],
                           'vals1': ['(27.0)', '1,025.0', '-'],
                           'vals2': ['(37.0)', '1,050.0', '-']},
                      index=['Portland', 'Berkeley', 'Cambridge'])
    df1 = df.mv.apply_to_columns("clean_str_to_float", ['vals', 'vals1'], fillna='0')
    assert df1.vals.dtype == float
    assert df1.vals2.dtype == object
    df2 = df.mv.apply_to_columns("clean_str_to_float", 'vals2', new_col='vals3', fillna='0')
    assert df2.vals3.dtype == float
    assert df2.vals2.dtype == object


def test_apply_to_columns(std_maeve_init_kwargs):
    # Test of this is done in clean_str above. This is to specifically test on a pandas (not Maeve) function
    s = Session(**std_maeve_init_kwargs)
    df = s.cook("TestLoadPandasCSVNoPipeline")
    df = df.mv.apply_to_columns("astype", ['artist_count', 'released_year'], dtype='str')
    assert df.artist_count.dtype == object
    assert df.released_year.dtype == object
    df = df.mv.apply_to_columns("astype", 'released_month', new_col='released_month_str', dtype='str')
    assert df.released_month_str.dtype == object


def test_repeat(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    update_rows = [
        {
            'change_cols': 'speechiness_%',
            'index': [0, 1],
            'replace_cols': 'liveness_%',
            'replace_index': [2, 3],
        },
        {
            'change_cols': 'speechiness_%',
            'index': [2, 3],
            'replace_val': 10,
        },
    ]
    df = s.cook("TestLoadPandasCSVNoPipeline")
    df = df.mv.repeat("replace_column_values", update_rows)
    assert df.loc[0, 'speechiness_%'] == 31
    assert df.loc[1, 'speechiness_%'] == 11
    assert df.loc[2, 'speechiness_%'] == 10
    assert df.loc[3, 'speechiness_%'] == 10
