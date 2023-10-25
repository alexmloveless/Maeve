from __future__ import annotations
from pydantic import (
    BaseModel,
    model_validator,
    Field,
    ValidationError
)
from typing import Literal, Optional, Union


class MplSubplotModel(BaseModel):
    figsize: Union[list, tuple] = (12, 6)
    gridspec: dict = {}