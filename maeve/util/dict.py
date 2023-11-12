import copy
import re
import string
import operator
from functools import reduce
from random import choices

from typing import Union

from maeve.util.log import Logger

class DictUtils:

    @classmethod
    def __mg(cls, a, b, always_override=None):
        """

        Parameters
        ----------
        a, b: dicts to merge

        Returns
        -------
        A dict B is merged on to dict A using the following rules:
        * For each key (k) in dict A.keys().union(B.keys())
            * if k is not in A then create A[k] with entire value of B[k]
            * if A[k] exists but B[k] does not, do nothing
            * if A[k] is a dict then run this algorithm for A[k] and B[k] (with no constraints on recursion)
                * if B[k] is not a dict, overwrite A[k] using B[k]
            * if A[k] is a list then loop through items i in list B[k]
                * if B[k] is not a list, overwrite A[k] using B[k]
                * if B[k][i] (when treated as an _entire object_) is in list A[k] then do nothing
                * if B[k][i] (when treated as an _entire object_) is NOT in list A[k] then append B[k][i] to A[k]

        """
        always_override = always_override if always_override else ["order_by"]
        override = b.get("override_keys", [])
        if type(override) is str:
            override = [override]
        elif type(override) is list:
            pass
        else:
            override = []

        override = set(override + list(always_override))

        keys = set(a.keys()).union(b.keys())
        for i in keys:
            if i in override:
                try:
                    a[i] = b[i]
                except KeyError:
                    # b[i] doesn't exist
                    continue
            # if they're dicts, merge
            if i in a.keys() and type(a[i]) is dict:
                try:
                    if type(b[i]) is not dict:
                        a[i] = b[i]
                        continue
                except KeyError:
                    # b[i] doesn't exist
                    continue
                if b[i].get("_mode", "merge") == "override":
                    del b[i]["_mode"]
                    a[i] = b[i]
                else:
                    try:
                        DictUtils.__mg(a[i], b[i])
                    except KeyError:
                        # b[i] doesn't exist
                        continue

            # if they're lists append unless b[i] is already in there
            elif i in a.keys() and type(a[i]) is list:
                try:
                    if type(b[i]) is not list:
                        a[i] = b[i]
                        continue
                except KeyError:
                    # b[i] doesn't exist
                    continue
                for x in b[i]:
                    if x in a[i]:
                        continue
                    else:
                        a[i].append(x)
            else:
                try:
                    a[i] = b[i]
                except KeyError:
                    # b[i] doesn't exist
                    continue

    @classmethod
    def mergedicts(cls, a: dict, b: dict, copy_a: bool = True, copy_b: bool = True) -> dict:
        """
        Overrides values from `a` with values from `b`. `a` and `b` need
        not have the same values. Values in b not in a.

        Parameters
        ----------
        a : dict
            The dict to merge into
        b : dict
            The dict to merge from

        Returns
        -------
        dict
            a merged dict

        """

        a = copy.deepcopy(a) if copy_a else a
        b = copy.deepcopy(b) if copy_b else b
        cls.__mg(a, b)

        return a

    @classmethod
    def search_dict(cls, d: dict, name: str, vals=None):
        if not vals:
            vals = set([])
        for k, v in d.items():
            if type(v) is dict:
                vals = cls.search_dict(v, name, vals=vals)
            else:
                if k == name:
                    vals.add(v)
        return vals

    @staticmethod
    def deep_dict(d: dict, path: list):
        return reduce(operator.getitem, path, d)

    @classmethod
    def order_dicts(
            cls,
            d: dict,
            log: Logger = None
    ) -> dict:
        log = log if log else Logger()
        if not type(d) == dict:
            log.warning(f"Expected dict but got {type(d)}")

        for k, v in d.items():
            if type(v) is dict:
                if "order_by" in v.keys():
                    if type(v["order_by"]) is list:
                        try:
                            d[k] = {k: v[k] for k in v["order_by"]}
                        except KeyError:
                            log.warning("List passed in order_by hay values not in the keys of the dict")
                    elif type(v["order_by"]) is str:
                        if v["order_by"] == "sort":
                            v = {k: d[k] for k in sorted(v["order_by"].keys())}
                v = cls.order_dicts(v)
        return d

    @staticmethod
    def parse_dotted_str(string):
        return re.split("[./]", string)

    @classmethod
    def dict_get_by_path(cls, root: dict, path: Union[list, tuple, str]):
        if type(path) is str:
            path = cls.parse_dotted_str(path)
        return reduce(operator.getitem, path, root)

    @classmethod
    def dict_set_by_path(cls, root, path, value):
        """Set a value in a nested object in root by item sequence."""
        if type(path) is str:
            path = cls.parse_dotted_str(path)
        cls.dict_get_by_path(root, path[:-1])[path[-1]] = value

    @classmethod
    def apply_overrides(cls, obj: dict, overrides: dict[str, Union[list, tuple, str]]):
        for path, value in overrides.items():
            cls.dict_set_by_path(obj, path, value)
        return obj

    @staticmethod
    def generate_random_key(chars: int = 10, charset: str = None) -> str:
        if not charset:
            charset = string.ascii_lowercase + string.digits
        return ''.join(choices(charset, k=chars))

