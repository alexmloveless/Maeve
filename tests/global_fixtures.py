import pytest
from maeve.models.core import GlobalConst
import json

g = GlobalConst()

basic_org_conf_loc = f"{g.package_root}/../tests/conf/basic_org_conf.hjson"
test_recipe_path_ = f"{g.package_root}/../tests/conf/recipes"
test_data_path_ = f"{g.package_root}/../tests/data/data"

dummy_local_org_conf = {
    "org": {
        "name": "Maeve PLC."
    },
    "env": {
        "recipes_root": test_recipe_path_,
        "paths": {
            "test_data": test_data_path_
        }
    }
}
dummy_local_org_conf_json = json.dumps(dummy_local_org_conf)

@pytest.fixture
def basic_org_conf():
    return basic_org_conf_loc


@pytest.fixture
def std_maeve_init_kwargs():
    return {
        "conf": dummy_local_org_conf_json,
        "log_level": "DEBUG",
        "log_location": "stdout"
    }

@pytest.fixture
def test_recipe_path():
    return test_recipe_path_

@pytest.fixture
def test_data_path():
    return test_data_path_

pytest_plugins = [
    "basic_org_conf",
    "std_maeve_init_kwargs",
    "test_recipe_path",
    "test_data_path",
]
