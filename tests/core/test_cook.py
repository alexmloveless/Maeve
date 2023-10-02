import pytest
from tests.global_fixtures import std_maeve_init_kwargs
from maeve import Session


def test_cook_csv(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    l = s.cook("TestSpotifyColumnsMin")
    assert type(l) is list
