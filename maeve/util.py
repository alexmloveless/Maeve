import maeve
from maeve.models.core import (
    GlobalConst, AnchorConst, FuncRecipe, LogConst,
    LocationRecipe, PipelineRecipe
)
from maeve.plugins.primitives import Primitives

from pydantic import ValidationError

import copy
from os import path, walk
import re
import json
import hjson
from functools import reduce
import operator
from typing import Union
from collections import deque
from datetime import datetime
import pandas as pd

g = GlobalConst()

class Logger:
    def __init__(
            self,
            log_level: str = None,
            log_location: str = None,
            log_maxlen: int = 1e+5
    ):
        self.g = LogConst()

        log_location = log_location if log_location else self.g.defualt_loc
        log_level = log_level if log_level else self.g.default_level
        self.loc = log_location

        self._levels = {v: level for level, v in enumerate(self.g.levels)}
        self.level = self._levels[log_level]
        self._log = deque([], int(log_maxlen))

    def debug(self, *args, **kwargs):
        self.log("DEBUG", *args, **kwargs)

    def info(self, *args, **kwargs):
        self.log("INFO", *args, **kwargs)

    def warning(self, *args, **kwargs):
        self.log("WARNING", *args, **kwargs)

    def error(self, *args, **kwargs):
        self.log("ERROR", *args, **kwargs)

    def critical(self, *args, **kwargs):
        self.log("CRITICAL", *args, **kwargs)

    def log(self, level, message, detail=''):
        if self._levels[level] >= self.level:

            if self.loc in ["catalogue", "both"]:
                self.add_to_log(level, message, detail)

            if self.loc in ["stdout", "both"]:
                print(f"{datetime.now()} {level} {message} {detail}")

    def add_to_log(self, level: str, source: str, message: str, detail: str = None):
        self._log.append({
            self.g.timestamp_label: datetime.now(),
            self.g.level_label: level,
            self.g.source_label: source,
            self.g.message_label: message,
            self.g.detail_label: detail
        })

    def get_log(self, fmt="df"):
        if fmt in ["df", "dataframe"]:
            return pd.DataFrame.from_records(self._log)
        else:
            return self._log


class DictUtils:

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
        override = b.get("override_keys", [])
        if type(override) is str:
            override = [override]
        elif type(override) is list:
            pass
        else:
            override = []

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

class FSUtils:

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
            raise RuntimeError(f"Unknown file extension for file {filepath}")

    @staticmethod
    def read_json_file(f):
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
            raise RuntimeError(f"Invalid or malformed JSON in file {f}")

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
            raise RuntimeError(f"Invalid or malformed HJSON in file {f}")



class AnchorUtils:
    ac = AnchorConst()

    @classmethod
    def resolve_anchors(cls,
                        cnf,  # Should be a confscade obj but a dict will actually work, but with limited recursion
                        obj: Union[list, dict],
                        env_conf,
                        anchors: dict = None) -> dict:

        # handle both dicts and lists
        try:
            iterator = obj.items()
        except AttributeError:
            iterator = enumerate(obj)

        anchors = anchors if anchors else {}

        for k, v in iterator:
            if type(v) in [dict, list]:
                cls.resolve_anchors(cnf, v, env_conf)
            elif type(v) is str:
                if re.match(cls.ac.match_regex, v):
                    identifier, keys = cls.parse_anchor(v)

                    if identifier in anchors.keys():
                        new_val = anchors[identifier]
                    else:
                        # grab a nested object
                        sub_conf = cnf.get(identifier)  # fully resolves the anchor incl. inheritance and nested anchors
                        if keys:
                            new_val = DictUtils.deep_dict(sub_conf, keys)
                        else:
                            new_val = sub_conf
                    if type(new_val) is dict:
                        new_val = cls.resolve_recipe(new_val, env_conf)
                    obj[k] = new_val
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

    @classmethod
    def resolve_recipe(cls, recipe, env_conf):
        if "recipe_type" not in recipe.keys():
            return recipe
        if recipe["recipe_type"] == "location":
            return LocationRecipe(paths=env_conf.paths, **recipe).model_dump()
        # if recipe["recipe_type"] == "pipeline":
        #     return PipelineRecipe(**recipe).model_dump()
        if recipe["recipe_type"] in ["dict", "list"]:
            return Primitives.primitive(recipe)

        return recipe


class FuncUtils:

    @classmethod
    def run_func(
            cls,
            recipe: Union[dict, FuncRecipe],
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
            recipe = FuncRecipe(**recipe)

        if obj is not None:
            # try and get the func from the obj namespace
            try:
                func = getattr(obj, recipe.function)
            except AttributeError:
                try:
                    func = getattr(ns, recipe.function)
                except AttributeError:
                    return cls.handle_func_fail(recipe, f"No known func called {recipe.function}", ret=obj)
                return cls._func(func, recipe, obj, logger)
            return cls._func(func, recipe, logger)
        else:
            try:
                func = getattr(ns, recipe.function)
            except AttributeError:
                cls.handle_func_fail(recipe, f"No known func called {recipe.function}")
            return cls._func(func, recipe, logger)

    @classmethod
    def _func(cls, func, recipe, obj=None, logger=None):
        try:
            if obj is None:
                return func(*recipe.args, **recipe.kwargs)
            else:
                return func(obj, *recipe.args, **recipe.kwargs)
        except Exception as e:
            return cls.handle_func_fail(recipe, e, logger=logger)

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
    def run_pipeline(cls,
                     recipe: Union[dict, list, maeve.models.core.PipelineRecipe],
                     session,
                     add_to_catalogue: bool = None,
                     obj=None
                     ):
        try:
            recipes = _recipes = PipelineRecipe(**recipe).model_dump()
            recipes = recipes["pipeline"]
        except ValidationError:
            recipes = _recipes = recipe

        if type(recipes) is dict:
            # keys are only there to help manage the order of funcs and facilitate merges
            recipes = recipes.values()
        else:
            recipes = recipes

        # we want to know if the caller actively set add_to_catalogue or that this is explicitly
        # set in the recipe one way or the other
        # Anything but a False value will evaluate as True
        # Recipe value takes precedence
        add_to_catalogue = _recipes.get("add_to_catalogue", add_to_catalogue)

        for r in recipes:
            # If the recipe is a string it will cook that recipe
            # and we assume that, since this isn't an inline recipe
            # or was an anchor somewhere upstream that it's a first-class
            # initialiser e.g. a loader.
            # In the instance that an object is passed, we don't trust this decision
            # since the object passed might not be what was expected since in
            # for example, loaders will pass the object through even if they point towards
            # a explicit data object on disk.
            # The recipe can still override this decision
            # Is this all a bit of a mess?
            if type(r) is str and add_to_catalogue is not False and obj is None:
                add_to_catalogue = True
            else:
                add_to_catalogue = False
            obj = session.cook(
                r,
                obj=obj,
                return_obj=True,
                add_to_catalogue=add_to_catalogue
            )

        return obj


class DemoUtils:
    @classmethod
    def add_demo_recipes(cls,
            loc: Union[list, dict, str],
            load_demo_recipes: bool
    ):
        if not load_demo_recipes:
            return loc

        d_root = g.package_paths["_demo_recipes_root"]

        if type(loc) is str:
            return [loc, d_root]
        elif type(loc) is list:
            loc.append(d_root)
            return loc
        elif type(loc) is dict:
            loc["demo_recipes"] = d_root
        else:
            return loc
