from pydantic import BaseModel
from typing import Literal, Optional, Union, Dict


class OrgConf(BaseModel):
    org_name: str = None
    org_defaults: dict = {}

class DataConf(BaseModel):
    data_root: Union[str, list] = None

class RecipesConf(BaseModel):
    config_root: Union[str, list] = None
