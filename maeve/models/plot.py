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
    nrows: int = 1
    ncols: int = 1
    recipe_type: Literal["mpl_subplots"] = "mpl_subplots"
    rcparams: dict = {}
    flattenax: bool = True
    as_obj: bool = False
    subplots_kwargs: dict = {}
    subplot_kw: Optional[MplSubplotkwModel] = MplSubplotkwModel()

    @model_validator(mode="after")
    def rm_recipe_type(self):
        del self.recipe_type
        return self


class MplPlotModel(BaseModel):
    recipe_type: Optional[Literal["mpl_plot"]] = "mpl_plot"
    plot_type: Optional[str] = None
    data_recipe: Optional[Union[str, dict]] = None
    subplots_kwargs: MplSubplotsModel = MplSubplotsModel()
    plot_kwargs: dict = {}

    @model_validator(mode="after")
    def rm_recipe_type(self):
        del self.recipe_type
        return self


