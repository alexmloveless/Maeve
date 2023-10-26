from __future__ import annotations
from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
    Field,
    ValidationError
)
from typing import Literal, Optional, Union, Sequence


class MplSubplotkwModel(BaseModel):
    model_config = ConfigDict(extra='allow')
    projection: Optional[Literal["mplot"]] = "mplot"


class MplGetSubplotsModel(BaseModel):
    recipe_type: Literal["mpl_subplots"]
    rcparams: dict = {}
    flattenax: bool = True
    subplot_kw: Optional[MplSubplotkwModel] = MplSubplotkwModel()

    @model_validator(mode="after")
    def rm_recipe_type(self):
        del self.recipe_type
        return self
