from maeve.util import FuncUtils
from maeve.models.core import DataRecipe, LoaderRecipe

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

    @staticmethod
    def stages(recipe, backend):
        load = LoaderRecipe(**recipe.load).model_dump()

        obj = FuncUtils.run_func(
            recipe=load,
            ns=backend
        )

        if recipe.process:
            obj = FuncUtils.run_pipeline(recipe.process, obj)

        if recipe.write:
            # placeholder
            pass

        return obj

    def load(self, recipe):
        pass
