from maeve.models.core import GlobalConst, AnchorConst, ConfConst
import logging
import copy
from os import path, walk
import re
import json
import hjson
import pkg_resources
from functools import reduce
import operator
from typing import Union

class Util:

    def get_logger(self, name: str, log_level: str = "WARNING"):

        LOG_LEVELS = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        logger = logging.getLogger(name)
        if log_level:
            logger.setLevel(LOG_LEVELS[log_level])
        return logger


class DictUtils:
    g = GlobalConst()

    @classmethod
    def __mg(cls, a, b):
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
        keys = set(a.keys()).union(b.keys())
        for i in keys:

            # if they're dicts, merge
            if i in a.keys() and type(a[i]) is dict:
                try:
                    if type(b[i]) is not dict:
                        a[i] = b[i]
                        continue
                except KeyError:
                    # b[i] doesn't exist
                    continue
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


class FSUtils:
    g = GlobalConst()

    @staticmethod
    def os_walk_and_filter(loc, dirregex: str = None, fileregex: str = None):
        """
        Recursively walk a file tree and filter based on args, returning a list of files
        Parameters
        ----------
        loc: str
            The location to start the search from
        dirregex: str
            Only directory names that match this regex will be traversed
        fileregex: str
            Only file names that match this regex will be traversed

        Returns
        -------
        A list of file names with their paths relative to the loc
        """
        files = []
        for i in walk(loc):
            if dirregex and not re.match(dirregex, i[0]):
                continue
            for j in i[2]:
                if fileregex and not re.match(fileregex, j):
                    continue
                files.append(path.join(i[0], j))
        return files

    @classmethod
    def read_conf_file(cls, filepath: str):
        """
        Reads a data file in various formats given a file location
        Will infer the file type from the file suffix
        Parameters
        ----------
        filepath: str
            Should be a fully qualified path

        Returns
        -------
        The contents for the file in dict form or None if it's not valid file path

        """
        if re.match(r".+\.json$", filepath):
            return cls.read_json_file(filepath)
        elif re.match(r".+\.hjson$", filepath):
            return cls.read_hjson_file(filepath)
        else:
            raise ValueError(f"Unknown file extension for file {filepath}")

    def read_json_file(self, f):
        """
        Reads a JSON file and returns in dict form
        Parameters
        ----------
        f: str
            Should be a fully qualified path
        Returns
        -------
        The contents for the file in dict form or None if it's not valid file path
        """
        try:
            with open(f, 'rb') as fh:
                return json.load(fh)
        except json.decoder.JSONDecodeError:
            return

    @staticmethod
    def read_hjson_file(f):
        """
        Reads an HJSON file and returns in dict form
        Parameters
        ----------
        f: str
            Should be a fully qualified path
        Returns
        -------
        The contents for the file in dict form or None if it's not valid file path
        """
        try:
            with open(f, 'rb') as fh:
                return hjson.load(fh, object_pairs_hook=dict)
        except hjson.scanner.HjsonDecodeError:
            raise TypeError(f"Invalid or malformed HJSON in file {f}")

    @classmethod
    def __list_package_dir(cls, item):
        for i in pkg_resources.resource_listdir(cls.g.package_name, item):
            new_item = item + "/" + i
            if pkg_resources.resource_isdir(cls.g.package_name, new_item):
                yield cls.__list_package_dir(i)
            else:
                yield new_item


class AnchorUtils:

    ac = AnchorConst()
    cc = ConfConst()
    g = GlobalConst()

    @classmethod
    def resolve_anchors(cls, cnf, obj: Union[list, dict]) -> dict:
        try:
            iterator = obj.items()
        except AttributeError:
            iterator = enumerate(obj)

        for k, v in iterator:
            if type(v) in [dict, list]:
                cls.resolve_anchors(cnf, v)
            elif type(v) is str:
                if re.match(cls.g.anchor_match_regex, v):
                    identifier, keys = cls.parse_anchor(v)
                    subcnf = cnf.get(identifier)
                    if keys:
                        obj[k] = DictUtils.deep_dict(subcnf, keys)
                    else:
                        obj[k] = cnf[cls.g.var_conf_value_field]
            else:
                continue
        return obj

    @classmethod
    def parse_anchor(cls, a):
        if not re.match(cls.ac.match_regex, a):
            raise ValueError("Not an anchor")
        anchor = re.sub(cls.ac.sub_regex, "", a)
        matches = re.split(r"\.", anchor)
        try:
            return matches[0], matches[1:]
        except KeyError:
            return matches[0], None


