import pytest
from tests.conf.recipes_fixtures import confscade_obj_base_test


def test_cs_default(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1")
    assert "cs_l1_str_1" in c.keys()


def test_cs_l1_anchor(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1")
    assert type(c["cs_l1_anchor1"]) is dict


def test_cs_inherits_nested_int(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1_inherits")
    assert c["cs_l1_dict_1"]["cs_l2_dict_1"]["cs_l2_dict_1_int_1"] == 3


def test_cs_inherits_list_append(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1_inherits")
    assert c["cs_l1_list_1"][3] == "cs_file_1_inherits_i4"


def test_cs_inherits_str_overwrite(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1_inherits")
    assert c["cs_l1_str_1"] == "v_l1_value_str_inherits"


def test_cs_inherits_anchor_overwrite(confscade_obj_base_test):
    # anchor two replaces anchor one and is resolved in its place
    c = confscade_obj_base_test.get("cs_file_1_inherits")
    assert c["cs_l1_anchor1"]["cs_anchor2_str1"] == "cs_anchor2_str1"


def test_cs_inherits_2_list_append(confscade_obj_base_test):
    c = confscade_obj_base_test.get("cs_file_1_inherits_2")
    assert c["cs_l1_list_1"][4] == "cs_file_1_inherits_2_i5"
