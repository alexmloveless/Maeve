from pydantic import BaseModel, model_validator, Field
from typing import Literal, Optional, Union

import os
from importlib import resources


###############################
#  Constants
###############################


class GlobalConst(BaseModel):
    package_name: str = "maeve"
    datapackagestub: str = "mv"
    package_root: str = Field(default_factory=lambda: str(resources.files("maeve")))


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

class FuncRecipe(BaseModel):
    function: str
    args: Optional[list] = []
    kwargs: Optional[dict] = {}
    fail_silently: bool = False


class LoaderRecipe(FuncRecipe):
    location: Union[str, dict]

    @model_validator(mode="after")
    def convert_to_func(self):
        if type(self.location) is dict:
            # TODO: Handle case where path is missing
            loc = self.location["path"]
        else:
            loc = self.location

        self.args.insert(0, loc)
        return self


class DataRecipe(BaseModel):
    backend: str = "pandas"
    load: dict = {}
    metadata: dict = {}
    process: Optional[Union[dict, list]] = None
    write: Optional[str] = None # think this always has to be a recipe name


class LocationRecipe(BaseModel):
    recipe_type: Literal["location"]
    use_path: Optional[str] = None
    path: str
    orig_path: Optional[str] = None
    paths: Optional[dict] = None

    @model_validator(mode="after")
    def resolve_path(self):
        if not self.paths:
            return self
        if self.use_path:
            self.orig_path = self.path
            try:
                self.path = os.path.join(self.paths[self.use_path], self.path)
            except KeyError:
                raise ValueError(f"root_path `{self.use_path}` not found in provided paths")
        return self


###############################
#  Model Meta
###############################

class ModelInfo:

    _alias_map = {
        "location": LocationRecipe
    }
    @classmethod
    def model_alias(cls, alias):
        return cls._alias_map[alias]

