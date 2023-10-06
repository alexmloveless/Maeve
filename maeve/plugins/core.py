from maeve.util import FuncUtils
from maeve.models.core import DataLoaderRecipe
import importlib


class Pipeline:
    def __init__(self, session):
        self.s = session

    def main(self, recipe, obj=None):
        return FuncUtils.run_pipeline(recipe, self.s, obj=obj)


class Function:
    def __init__(self, session):
        self.s = session

    def main(self, recipe, obj=None):
        return FuncUtils.run_func(recipe, obj=obj)


class DataLoader:
    def __init__(self, session):
        self.s = session

    def main(self, recipe, obj=None):
        if obj is not None:
            return obj
        recipe = DataLoaderRecipe(**recipe).model_dump()
        backend = self.get_backend(recipe["backend"])
        return FuncUtils.run_func(
            recipe,
            ns=backend
        )

    @staticmethod
    def get_backend(backend):
        return importlib.import_module(backend)
