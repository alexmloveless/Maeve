import pytest
from maeve.models.core import GlobalConst
from maeve.conf import Confscade

g = GlobalConst()

recipes_root = f"{g.package_root}/../tests/conf/recipes"
confscade_tests_paths_ = [
    recipes_root + "/confscade.hjson"
]

confscade_tests_pipeline_recipes = recipes_root + "/pipelines.hjson"

@pytest.fixture
def confscade_test_paths():
    return confscade_tests_paths_

@pytest.fixture
def confscade_obj_base_test():
    return Confscade(confscade_tests_paths_, log_level="DEBUG", log_location="stdout")

@pytest.fixture
def confscade_obj_pipeline_test():
    return Confscade(confscade_tests_pipeline_recipes, log_level="DEBUG", log_location="stdout")

pytest_plugins = [
    "confscade_test_paths",
    "confscade_obj_base_test",
    "confscade_obj_pipeline_test"
]