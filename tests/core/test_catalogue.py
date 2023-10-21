import pytest
from tests.global_fixtures import std_maeve_init_kwargs, test_data_path
from maeve import Session


def test_pandas_load_cat_exists(std_maeve_init_kwargs):
    s = Session(**std_maeve_init_kwargs)
    recipe_name = "TestLoadPandasCSVNoPipeline"
    recipe = s.recipes.get(recipe_name)
    recipe_hash = s.c.generate_obj_hash(recipe)
    df = s.cook(recipe_name)
    cdf = s.c.names[recipe_name]
    cdf = s.c.get(recipe, method="obj")
    assert recipe_hash in s.c.hashes.keys()

