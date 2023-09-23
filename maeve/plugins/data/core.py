from maeve.util import FuncUtils
from maeve.models.core import DataLoader, DataRecipe

from pydantic import BaseModel
from typing import get_type_hints, Optional, Union
import importlib


class Data:
    def __init__(self, session=None):
        self.s = session

    def main(self, recipe: dict):
        recipe = DataRecipe(**recipe)
        backend = Data.get_backend(recipe.backend)
        obj = self.stages(recipe, backend)
        return obj

    @staticmethod
    def get_backend(backend):
        return importlib.import_module(backend)

    def stages(self, recipe, backend):
        try:
            loc = recipe.load.location
        except AttributeError:
            # complain
            pass
        # add loc to args then run run_func()
        df = getattr(backend, recipe.load.loader)(
            loc, *recipe.load.args, **recipe.load.kwargs
        )
        # need to adjust anchor utils so that it can handle "special" variables, the first being "location"
        # which will have a "use_root" field that will be used to prepend the value
        obj = FuncUtils.run_func(
            recipe=recipe.load.loader
        )
        if recipe.load:
            pass
        if recipe.process:
            pass
        if recipe.write:
            pass

        return df

    def load(self, recipe):
        pass

class Loaders:
    def __init__(self, recipe: BaseModel):
        self.backend = recipe.load.backend

    @classmethod
    def load(cls, recipe):
        return getattr(cls, recipe.load.loader)(recipe)

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