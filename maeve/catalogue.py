import pandas
from pydantic import BaseModel
from typing import Any, Optional, Literal, Union
from maeve.util import DictUtils
import re
import hashlib
import json
from datetime import datetime
import string
from pandas.util import hash_pandas_object
from copy import deepcopy

class CatalogueItemModel(BaseModel):
    obj: Any
    name: Optional[str] = None
    recipe_hash: Optional[str] = None
    raw_recipe_hash: Optional[str] = None
    obj_hash: Optional[str] = None
    metadata: Optional[dict] = None


class Catalogue:

    def __init__(self, logger):
        self.log = logger
        self.alpha = string.ascii_lowercase + string.digits
        self.obj = {}
        self.names = {}
        self.hashes = {}

    def add(self,
            obj: Any,
            recipe: dict = None,
            name: str = None,
            metadata: dict = None,
            on_exists: Literal["return", "replace"] = "replace",
            copy_obj: bool = True,
            hash_recipe_with_obj: bool = True,
            return_item: Literal["id", "object"] = "id"
            ):

        # to get round the whole truth of df is ambiguous thing
        have_obj = True if obj is not None else False

        obj_hash = None
        if have_obj:
            if copy_obj:
                obj = deepcopy(obj)
            try:
                obj_hash = self.generate_obj_hash(obj)
            except ValueError:
                obj_hash = None

        if recipe:
            recipe_hash = self.generate_obj_hash(recipe)
            raw_recipe_hash = recipe_hash
            if on_exists == "return":
                try:
                    return self.get(recipe_hash, method="hash")
                except ValueError:
                    pass
                if have_obj and hash_recipe_with_obj:
                    self.log.debug("Using recipe + obj recipe_hash")
                    recipe_hash = recipe_hash + obj_hash
        else:
            self.log.debug("No recipe_hash generated")
            recipe_hash = raw_recipe_hash = None

        metadata = self.generate_metadata(metadata)
        catalogue_item = CatalogueItemModel(
            obj=obj,
            name=name,
            recipe_hash=recipe_hash,
            raw_recipe_hash=raw_recipe_hash,
            obj_hash=obj_hash,
            metadata=metadata
        )
        key = self._add(catalogue_item)
        if return_item == "id":
            return key
        else:
            return catalogue_item

    def _add(self, item):
        key = DictUtils.generate_random_key(charset=self.alpha)
        self.obj[key] = item
        self.names[item.name] = item
        self.hashes[item.recipe_hash] = item
        self.hashes[item.obj_hash] = item
        return key


    def increment_name(self, name):
        try:
            n = int(re.match("_(\d+)$", name).groups()[0])
        except AttributeError:
            return name + "_1"

        return re.sub(r"\d+$", str(n + 1), name)

    def has(self, name):
        if name in self.obj.keys():
            return True
        else:
            return False

    def get(self,
            obj: Any,
            method: Literal["hash", "name", "id", "obj"],
            return_obj: bool = True
            ):
        funcmap = {
            "hash": self.get_using_hash,
            "name": self.get_using_name,
            "id": self.get_using_id,
            "obj": self.get_using_obj
        }
        if method not in funcmap.keys():
            raise ValueError("Unknown method")
        try:
            item = funcmap[method](obj)
        except KeyError:
            raise ValueError(f"No item with that {method} in the catalogue")
        if return_obj:
            if method in ["hash", "id"]:
                return item.obj
            else:
                if type(item) is list:
                    return item
                else:
                    return item.obj
        else:
            return item

    def get_using_hash(self, item: int, gen_hash=False):
        if gen_hash:
            item = self.generate_obj_hash(item)
        return self.hashes[item]

    def get_using_obj(self, item):
        return self.get_using_hash(item, gen_hash=True)

    def get_using_name(self, name: str):
        return self.names[name]

    def get_using_id(self, catalogue_id: str):
        return self.obj[catalogue_id]

    def generate_obj_hash(self, obj):
        if type(obj) is pandas.core.frame.DataFrame:
            self.log.debug("Generating hash from pandas DataFrame")
            return hashlib.sha256(hash_pandas_object(obj, index=True).values).hexdigest()
        elif type(obj) is dict:
            self.log.debug("Generating hash from pandas dict")
            return hashlib.sha256(json.dumps(obj, sort_keys=True).encode("utf-8")).hexdigest()
        else:
            return hashlib.sha256(str(obj).encode("utf-8")).hexdigest()

    def generate_metadata(self, metadata: dict = None):
        metadata = metadata if metadata else {}
        _metadata = {
            "created" : datetime.now()
        }
        return {**metadata, **metadata}


class Register:
    def __init__(self):
        self.env = None
        self._org = None
        self.org = None
