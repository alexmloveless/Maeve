from maeve.util import FuncUtils
from maeve.models.core import DataRecipe, LoaderRecipe

import importlib

from typing import Optional

class Data:
    def __init__(self, session=None):
        self.s = session

    def load(self, recipe: dict):
        recipe = DataRecipe(**recipe)
        backend = Data.get_backend(recipe.backend)
        obj = self.stages(recipe, backend)
        return obj

    # an alias so that we have the standard plugin interface method
    main = load

    def query_parquet(
        self,
        recipe: dict,
        columns: Optional[list] = None,
        filters: Optional[list] = None
    ):
        pass

    @staticmethod
    def get_backend(backend):
        return importlib.import_module(backend)

    def stages(self, recipe, backend):
        if recipe.load["function"] == "recipe":
            obj = self.s.cook(
                recipe.load["recipe"],
                return_obj=True,
                use_from_catalogue=True
            )
        else:
            load = LoaderRecipe(**recipe.load).model_dump()
            obj = FuncUtils.run_func(
                load,
                ns=backend
            )

        if recipe.process:
            obj = FuncUtils.run_pipeline(recipe.process, obj)

        if recipe.write:
            # placeholder
            pass

        return obj
