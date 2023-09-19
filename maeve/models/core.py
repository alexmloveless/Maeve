from pydantic import BaseModel
from typing import Literal, Optional, Union, Dict

###############################
#  Constants
###############################


class GlobalConst(BaseModel):
    package_name: str = "maeve"
    datapackagestub: str = "mv"

    class Config:
        frozen = True


class ConfConst(BaseModel):
    var_value_field: str = "value"

    class Config:
        frozen = True


class AnchorConst(BaseModel):
    prefix: str = "@"
    match_regex: str = r"^@[\w+]"
    sub_regex: str = r"^@"

    class Config:
        frozen = True


###############################
#  Mutable models
###############################
class OrgConf(BaseModel):
    org_name: str = None
    org_defaults: dict = {}


class EnvConf(BaseModel):
    name: str = "default"
    type: Optional[str] = None


class DataConf(BaseModel):
    data_root: Union[str, list] = None


class RecipesConf(BaseModel):
    config_root: Union[str, list] = None


class LocConf(BaseModel):
    name: str


class ConfscadeDefaults(BaseModel):
    GLOBAL_DEFAULT_CONF: Optional[dict] = {"default" : {}}
    RECURSIVE_FLAG: Optional[bool] = True
    DEFAULT_CONF_KEY: Optional[str] = "default"
    MINIMUM_CONF: Optional[dict] = {}
    ERROR_ON_NOTFOUND: Optional[bool] = False
    OUTPUT_DATETIME_FMT: Optional[str] = "%Y-%m-%d %H:%M:%S"
