from pydantic import BaseModel
from typing import Literal, Optional, Union, Dict


class DataAccessLoadGeneric(BaseModel):
    loader: str
    backend: Literal["pandas", "polars"] = "pandas"
    location: Optional[str] = None
    filters: Optional[list] = None
    columns: Optional[list] = None
    pipeline: Optional[str, list] = None


class DataAccessConf(BaseModel):
    conf_type: Literal["data_access"]
    metadata: Optional[dict] = {}
    load: DataAccessLoadGeneric
    pipeline: Optional[str, list] = None


class PipelineStageConf(BaseModel):
    function: str
    args: Optional[list] = []
    kwargs: Optional[dict] = {}
    raise_on_except: Optional[bool] = False


class PipelineConf(BaseModel):
    conf_type: Literal["pipeline"]
    metadata: Optional[dict] = {}
    stages: Dict[PipelineStageConf]


class Models:
    def __init__(self):
        self._model_map = {
            "data_access": DataAccessConf
        }

    @property
    def model_map(self):
        return self._model_map

    def get(self, name):
        return self._model_map[name]
