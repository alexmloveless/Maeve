import pytest

basic_org_conf_loc = "../conf/basic_org_conf.hjson"

@pytest.fixture
def basic_org_conf():
    return basic_org_conf_loc


@pytest.fixture
def std_maeve_init_kwargs():
    return {
        "conf": basic_org_conf_loc,
        "log_level": "DEBUG",
        "log_location": "stdout"
    }


pytest_plugins = [
    "std_maeve_init_kwargs"
]
