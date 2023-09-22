from .backends.pandas import PandasLoaders
from .backends.polars import PolarsLoaders

from pydantic import BaseModel
from typing import get_type_hints, Optional, Union


class Loader(BaseModel):
    type: str
    backend: str = "pandas"
    location: Optional[str] = None
    filters: Optional[list] = None
    columns: Optional[list] = None
    process: Optional[Union[dict, list, str]] = None
    use_data_root: bool = True

class DataRecipe(BaseModel):
    metadata: dict = {}
    load: Optional[dict] = None
    process: Optional[Union[dict, list, str]] = None
    write: Optional[str] = None # think this always has to be a recipe name

class Data:
    def __init__(self, session=None):
        self.s = session

    def main(self, recipe: dict):
        recipe = DataRecipe(**recipe)
        self.stages(recipe)

    def stages(self, recipe):
        if recipe.load:
            pass
        if recipe.process:
            pass
        if recipe.write:
            pass

    def load(self, recipe):
        pass

class Loaders:

    def loader(func):
        # loader decorator that parses the model etc.
        def inner(*args, **kwargs):
            hints = get_type_hints(func) # possible routing dependent on args
            return func(*args, **kwargs)
        return inner

    @loader
    @staticmethod
    def csv(recipe):
        pass