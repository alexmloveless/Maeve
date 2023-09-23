from maeve.models.core import GlobalConst, AnchorConst, ConfConst, FuncConf
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
from collections import deque
from datetime import datetime

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


class Logger:
    def __init__(self, name, reg, log_level="WARNING", log_maxlen=1e+5):
        self.name = name
        self.reg = reg
        if not hasattr(reg, name):
            setattr(reg, name, deque([], int(log_maxlen)))

        self._levels = {v: l for l, v in enumerate(
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )}
        self.level = self._levels[log_level]

    def debug(self, *args, **kwargs):
        self.log("DEBUG", *args, **kwargs)
    def info(self, *args, **kwargs):
        self.log("INFO", *args, **kwargs)
    def warning(self, *args, **kwargs):
        self.log("WARNING", *args, **kwargs)
    def error(self, *args, **kwargs):
        self.log("error", *args, **kwargs)
    def critical(self, *args, **kwargs):
        self.log("critical", *args, **kwargs)

    def log(self, level, source, message, detail=None):
        if self._levels[level] >= self.level:
            self.add_to_log(level, source, message, detail)

    def add_to_log(self, level: str, source: str, message: str, detail: str = None):
        getattr(self.reg, self.name).append((
            datetime.now(),
            level,
            source,
            message,
            detail
        ))


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
    def resolve_anchors(cls, cnf, obj: Union[list, dict], anchors: dict = None) -> dict:
        try:
            iterator = obj.items()
        except AttributeError:
            iterator = enumerate(obj)

        anchors = anchors if anchors else {}

        for k, v in iterator:
            if type(v) in [dict, list]:
                cls.resolve_anchors(cnf, v)
            elif type(v) is str:
                if re.match(cls.g.anchor_match_regex, v):
                    identifier, keys = cls.parse_anchor(v)

                    if identifier in anchors.keys():
                        obj[k] = anchors[identifier]
                    else:
                        subcnf = cnf.get(identifier)
                        if keys:
                            obj[k] = DictUtils.deep_dict(subcnf, keys)
                        else:
                            obj[k] = cnf
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

class FuncUtils:

    @classmethod
    def run_func(
            cls,
            recipe: Union[dict, FuncConf],
            obj=None,
            ns=None,
            logger=None
    ):
        """
            Either obj or ns (or both) must be passed
            If ns is not passed, all functions must
            exist in the object namespace
        """
        if type(recipe) is dict:
            recipe = FuncConf(**recipe)

        if obj is not None:
            # try and get the func from the obj namespace
            try:
                func = getattr(obj, recipe.function)
            except AttributeError:
                try:
                    func = getattr(ns, recipe.function)
                except AttributeError:
                    cls.handle_func_fail(recipe, f"No know func called {recipe.function}")
            return cls._func(func, recipe, obj, logger)
        else:
            try:
                func = getattr(ns, recipe.function)
            except AttributeError:
                cls.handle_func_fail(recipe, f"No know func called {recipe.function}")
            return cls._func(func, recipe, obj, logger)

    @classmethod
    def _func(cls, func, recipe, obj=None, logger=None):
        try:
            if obj is None:
                return func(*recipe.args, **recipe.kwargs)
            else:
                return func(obj, *recipe.args, **recipe.kwargs)
        except Exception as e:
            _ = cls.handle_func_fail(recipe, e, logger=logger)
            return obj

    @staticmethod
    def handle_func_fail(recipe, e, ret=None, logger=None):
        message = f"Pipeline function {recipe.function} failed with error {e}"
        if recipe.fail_silently:
            if logger:
                logger.info(message)
            else:
                print(message)
            return ret
        else:
            raise RuntimeError(message)


    @classmethod
    def run_pipeline(cls, conf: Union[dict, list, str], obj=None):
        if type(conf) is dict:
            # keys are only there to help manage the order of funcs
            conf = conf.values()
        elif type(conf) is str:
            # assume it's a reference to a pipeline conf
            pass
        else:
            raise ValueError("Unknown data type for pipeline conf")

        for f in conf:
            obj = FuncUtils.run_func(obj, conf)
