import pytest
from tests.global_fixtures import std_maeve_init_kwargs
from maeve import Session
import pandas as pd
import os
import sys




@pytest.fixture
def maeve_session(std_maeve_init_kwargs):
    print(os.path.dirname(os.path.abspath(__file__)))
    return Session(**std_maeve_init_kwargs)


def test_load_csv(maeve_session):
    df = maeve_session.cook("TestLoadCSVNoPipeline")
    assert type(df) is pd.core.frame.DataFrame