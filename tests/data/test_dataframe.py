import pytest
from tests.global_fixtures import std_maeve_init_kwargs, basic_org_conf
from maeve import Session
import pandas as pd
import os


@pytest.fixture
def maeve_session(std_maeve_init_kwargs):
    return Session(**std_maeve_init_kwargs)


def test_load_csv(maeve_session):
    df = maeve_session.cook("TestLoadCSVNoPipeline")
    assert type(df) is pd.core.frame.DataFrame