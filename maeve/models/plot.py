from __future__ import annotations
from pydantic import (
    BaseModel,
    model_validator,
    Field,
    ValidationError
)
from typing import Literal, Optional, Union


class MplSubplotModel(BaseModel):
    rcparams: dict