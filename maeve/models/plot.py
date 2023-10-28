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


class MplSubplotsModel(BaseModel):
    recipe_type: Literal["mpl_subplots"] = "mpl_subplots"
    rcparams: dict = {}
    flattenax: bool = True
    subplot_kw: Optional[MplSubplotkwModel] = MplSubplotkwModel()

    @model_validator(mode="after")
    def rm_recipe_type(self):
        del self.recipe_type
        return self

class MplPlotModel(BaseModel):
    recipe_type: Literal["mpl_plot"]
    plot_type: Optional[str] = None
    data_recipe: Optional[Union[str, dict]] = None
    subplots_kwargs: MplSubplotsModel = MplSubplotsModel()
    plot_kwargs: dict = {}

    @model_validator(mode="after")
    def rm_recipe_type(self):
        del self.recipe_type
        return self
