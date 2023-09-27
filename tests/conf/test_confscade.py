import pytest
from tests.conf.recipes_fixtures import confscade_obj_base_test


def test_confscade_default(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1")
    assert "cs1_l1_str_1" in c.keys()


def test_confscade_l1_anchor(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1")
    assert type(c["cs1_l1_anchor1"]) is dict
