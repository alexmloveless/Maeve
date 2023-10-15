from __future__ import annotations
from pydantic import BaseModel, model_validator, Field, ValidationError, ImportString
from typing import Literal, Optional, Union, Dict, List

import os
from importlib import resources

import maeve.util


###############################
#  Constants
###############################

class PackageInfo:
    def __init__(self):
        self._package_root = str(resources.files("maeve"))
        self._demo_recipes_root = os.path.join(self._package_root, "recipebook/demo_recipes/")
        self._package_data_recipes_root = os.path.join(self._package_root, "recipebook/data/")
        self._package_test_recipes_root = os.path.join(self._package_root, "../tests/conf/recipes/")

    @property
    def package_root(self):
        return self._package_root

    @property
    def demo_recipes_root(self):
        return self._demo_recipes_root

    @property
    def package_data_recipes_root(self):
        return self._package_data_recipes_root

    @property
    def package_test_recipes_root(self):
        return self._package_test_recipes_root


_pinfo = PackageInfo()


class GlobalConst(BaseModel):
    package_name: str = "maeve"
    datapackagestub: str = "mv"
    package_root: str = Field(_pinfo.package_root)
    package_paths: dict = {
        "_package_root": _pinfo.package_root,
        "demo_recipes" : _pinfo.demo_recipes_root,
        "data_recipes" : _pinfo.package_data_recipes_root,
        "test_recipes" : _pinfo.package_test_recipes_root
    }

    class Config:
        frozen = True


class ConfConst(BaseModel):
    type_field: str = "recipe_type"
    init_params_field: str = "init_params"
    plugin_delim: str = r"\."
    plugin_default_entrypoint: str = "main"

    class Config:
        frozen = True


class AnchorConst(BaseModel):
    prefix: str = "@"
    match_regex: str = r"^@[\w+]"
    sub_regex: str = r"^@"
    root_paths_attrs: dict = {
            "data_root": "data_root",  # should mirror name in EnvConf
            "recipes_root": "recipes_root"  # should mirror name in EnvConf
        }

    class Config:
        frozen = True


class LogConst(BaseModel):
    levels: list = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    default_level: str = "WARNING"
    defualt_loc: str = "stdout"
    timestamp_label: str = "Timestamp"
    level_label: str = "Level"
    source_label: str = "Source"
    message_label: str = "Message"
    detail_label: str = "Detail"

    class Config:
        frozen = True

class ConstValidator(BaseModel):
    core: dict = {}
    conf: dict = {}
    anchor: dict = {}


class Globals:
    def __init__(self, **kwargs):
        self.models = ConstValidator(**kwargs)
        self.core = GlobalConst(**self.models.core)
        self.conf = ConfConst(**self.models.conf)
        self.anchor = AnchorConst(**self.models.anchor)


###############################
#  Mutable models
###############################
class OrgConf(BaseModel):
    org_name: str = None
    org_defaults: dict = {}


class EnvConf(BaseModel):
    name: str = "default"
    log_maxlen: int = int(1e+5)
    type: Optional[str] = None
    recipes_root: Union[str, dict] = None
    paths: Union[dict] = {}
    load_package_recipes: list = [
        "demo_recipes",
        "data_recipes"
    ]
    load_test_recipes: bool = False
    @model_validator(mode="after")
    def test_recipes(self):
        if self.load_test_recipes:
            self.load_package_recipes.append("test_recipes")
        return self



class PluginParams(BaseModel):
    class_args: list = []
    class_kwargs: dict = {}


class ConfscadeDefaults(BaseModel):
    GLOBAL_DEFAULT_CONF: Optional[dict] = {"default" : {}}
    RECURSIVE_FLAG: Optional[bool] = True
    DEFAULT_CONF_KEY: Optional[str] = "default"
    MINIMUM_CONF: Optional[dict] = {}
    ERROR_ON_NOTFOUND: Optional[bool] = False
    OUTPUT_DATETIME_FMT: Optional[str] = "%Y-%m-%d %H:%M:%S"

########################################################
# Recipe Models
########################################################


class FuncRecipe(BaseModel):
    recipe_type: Optional[Union[Literal["function"], Literal["data_loader"]]] = "function"
    function: str
    args: Optional[list] = []
    kwargs: Optional[dict] = {}
    add_to_catalogue: bool = False
    catalogue_name: Optional[str] = None
    fail_silently: bool = False


class DataLoaderRecipe(FuncRecipe):
    recipe_type: Literal["data_loader"] = "data_loader"
    location: Union[str, dict]
    backend: str = "pandas"

    @model_validator(mode="after")
    def convert_to_func(self):
        if type(self.location) is dict:
            # TODO: Handle case where path is missing
            loc = self.location["path"]
        else:
            loc = self.location

        self.args.insert(0, loc)
        return self


class LocationRecipe(BaseModel):
    recipe_type: Literal["location"] = "location"
    use_path: Optional[str] = None
    path: str
    orig_path: Optional[str] = None
    paths: Optional[dict] = None

    @model_validator(mode="after")
    def resolve_path(self):
        g = GlobalConst()
        if not self.paths:
            return self
        self.orig_path = self.path
        if self.use_path:
            if self.use_path in g.package_paths.keys():
                new_path = g.package_paths[self.use_path]
            else:
                try:
                    new_path = self.paths[self.use_path]
                except KeyError:
                    raise ValueError(f"root_path `{self.use_path}` not found in provided paths")
            self.path = os.path.join(new_path, self.path)
        return self


class PipelineRecipe(BaseModel):
    recipe_type: Literal["pipeline"] = "pipeline"
    # pipeline: Union[dict[str, Union[PipelineRecipe, DataLoaderRecipe, FuncRecipe]],
    #                 list[Union[PipelineRecipe, DataLoaderRecipe, FuncRecipe]]]
    pipeline: Union[str, dict[str, Union[dict, str]], list[Union[dict, str]]]


###############################
#  Model Meta
###############################

class ModelInfo:

    _model_map = {
        "location": LocationRecipe,
        "pipeline": PipelineRecipe,
        "function": FuncRecipe,
        "loader": DataLoaderRecipe
    }

    @classmethod
    def model(cls, alias):
        return cls._model_map[alias]

    @classmethod
    def identify_model(cls, recipe: dict, log: maeve.util.Logger = None):
        for model in cls._model_map.values():
            try:
                m = model(**recipe)
                if log:
                    log.debug(f"Recipe identified as {m.recipe_type}")
                return m.recipe_type
            except ValidationError:
                continue

        raise ValueError("Unable to determine recipe type")




