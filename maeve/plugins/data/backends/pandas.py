from pydantic import BaseModel, field_validator, conlist
from typing import Optional, Union


class PandasSlicerModel(BaseModel):
    index: Optional[Union[conlist(Union[int, str, None], min_length=1, max_length=3), str, int]] = None
    columns: Optional[Union[conlist(Union[int, str, None], min_length=1, max_length=3), str, int]] = None

    @field_validator('index', 'columns')
    @classmethod
    def create_slice(cls, v: Union[list, str]):
        if type(v) in [str, int]:
            v = [v]
        return slice(*v)

class PandasDataFrame:
    def __init__(self):
        pass

    def loc_slice(self, df, index=None, columns=None):
        mod = PandasSlicerModel(index=index, columns=columns)
        return df.loc[mod.index, mod.columns]

    def iloc_slice(self, df, index=None, columns=None):
        mod = PandasSlicerModel(index=index, columns=columns)
        return df.iloc[mod.index, mod.columns]
