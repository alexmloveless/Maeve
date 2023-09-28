import pytest
from tests.conf.recipes_fixtures import confscade_obj_base_test


def test_cs_default(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1")
    assert "cs1_l1_str_1" in c.keys()


def test_cs_l1_anchor(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1")
    assert type(c["cs1_l1_anchor1"]) is dict


def test_cs_inherits_nested_int(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1_inherits")
    assert c["cs1_l1_dict_1"]["cs1_l2_dict_1"]["cs1_l2_dict_1_int_1"] == 3
