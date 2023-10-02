import pytest
from maeve.models.core import GlobalConst
from maeve import Session
import json

g = GlobalConst()

basic_org_conf_loc = f"{g.package_root}/../tests/conf/basic_org_conf.hjson"

dummy_local_org_conf = {
    "org": {
        "name": "Maeve PLC."
    },
    "env": {
        "recipes_root": f"{g.package_root}/../tests/conf/recipes",
        "paths": {
            "test_data": f"{g.package_root}/../tests/data/data"
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


pytest_plugins = [
    "basic_org_conf",
    "std_maeve_init_kwargs",
]
