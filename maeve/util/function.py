from typing import Any, Union
from pydantic import ValidationError
from maeve.models.core import FuncRecipe, GlobalConst, PipelineRecipe


class FuncUtils:
    g = GlobalConst()

    @classmethod
    def run_func(cls,
                 function: str,
                 obj: Any = None,
                 ns: Any = None,
                 func_args=None,
                 func_kwargs=None,
                 fail_silently: bool = False,
                 logger=None
                 ):

        func_args = func_args if func_args else []
        func_kwargs = func_kwargs if func_kwargs else {}
        if obj is not None:
            # try and get the func from the obj namespace
            try:
                func = getattr(obj, function)
            except AttributeError:
                func = cls._try_namespaces(function, obj, ns=ns)

            return cls._func(func, logger=logger, *func_args, **func_kwargs)
        else:
            try:
                func = getattr(ns, function)
            except AttributeError:
                cls.handle_func_fail(
                    f"No known func called {function}",
                    function,
                    fail_silently=fail_silently
                )
            return cls._func(func, logger=logger, *func_args, **func_kwargs)

    @classmethod
    def run_func_recipe(
            cls,
            recipe: Union[dict, FuncRecipe],
            obj=None,
            ns=None,
            logger=None
    ):
        """
            Either obj or ns (or both) must be passed
            If ns is not passed, all functions must
            exist in the object namespace
        """
        if type(recipe) is dict:  # noqa: E721
            recipe = FuncRecipe(**recipe)

        ns = recipe.namespace if recipe.namespace else ns

        args = recipe.args
        kwargs = recipe.kwargs
        return cls.run_func(
            recipe.function,
            func_args=args,
            obj=obj,
            ns=ns,
            fail_silently=recipe.fail_silently,
            logger=logger,
            func_kwargs=kwargs
        )

    @classmethod
    def _try_namespaces(cls, function: str, obj: Any, ns=None, fail_silently=False, logger=None):
        if ns:
            try:
                return getattr(ns, function)
            except AttributeError:
                return cls.handle_func_fail(
                    f"No known func called {function} in given namespace",
                    function, ret=obj, logger=logger)
        if obj is not None:
            if ns:
                namespaces = [ns]
            else:
                namespaces = cls.g.func_namespaces
            for n in namespaces:
                try:
                    _ns = getattr(obj, n)
                except AttributeError:
                    continue
                try:
                    return getattr(_ns, function)
                except AttributeError:
                    continue
        return cls.handle_func_fail(
            f"No known func called {function} in any namespace",
            function,
            ret=obj,
            fail_silently=fail_silently,
            logger=logger
        )

    @classmethod
    def _func(cls, func, *args, obj=None, logger=None, **kwargs):
        try:
            if obj is None:
                return func(*args, **kwargs)
            else:
                return func(obj, *args, **kwargs)
        except Exception as e:
            return cls.handle_func_fail(e, func, logger=logger)

    @staticmethod
    def handle_func_fail(e, function, fail_silently: bool = False, ret=None, logger=None):
        message = f"Pipeline function {function} failed with error {e}"
        if fail_silently:
            if logger:
                logger.info(message)
            else:
                print(message)
            return ret
        else:
            raise RuntimeError(message)

    @classmethod
    def run_pipeline(cls,
                     recipe: Union[dict, list, PipelineRecipe],
                     session,
                     obj=None
                     ):
        try:
            recipes = _recipes = PipelineRecipe(**recipe).model_dump()
            recipes = recipes["pipeline"]
        except ValidationError:
            recipes = _recipes = recipe

        if type(recipes) is dict:  # noqa: E721
            # keys are only there to help manage the order of funcs and facilitate merges
            recipes = recipes.values()
        else:
            recipes = recipes

        for r in recipes:
            # if obj is None then this must be a loader, therefore we want to add it to the catalogue
            # Otherwise this is just a stage, so we only add if explicitly told to do so (see below)
            add_to_catalogue = True if obj is None else False
            use_from_catalogue = True if obj is None else False

            # Recipe value takes precedence in all cases
            if type(r) is dict:
                add_to_catalogue = r.get("add_to_catalogue", add_to_catalogue)
            obj = session.cook(
                r,
                obj=obj,
                return_obj=True,
                add_to_catalogue=add_to_catalogue,
                use_from_catalogue=use_from_catalogue
            )

        return obj
