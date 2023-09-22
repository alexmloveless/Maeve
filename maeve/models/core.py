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
    type_field: str = "type"
    init_params_field: str = "init_params"
    plugin_delim: str = r"\."
    plugin_default_entrypoint: str = "main"

    class Config:
        frozen = True


class AnchorConst(BaseModel):
    prefix: str = "@"
    match_regex: str = r"^@[\w+]"
    sub_regex: str = r"^@"

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
        self.conf = GlobalConst(**self.models.conf)
        self.anchor = GlobalConst(**self.models.anchor)


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
    data_root: Union[str, list] = None
    recipes_loc: Union[str, list] = None


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
