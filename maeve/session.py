from maeve.util import Logger, RecipeUtils, DictUtils
from maeve.plugins import Plugins
from maeve.models.core import Globals, OrgConf, EnvConf, PluginParams, ModelInfo, DataLoaderRecipe
from maeve.conf import Confscade
from maeve.catalogue import Catalogue, Register

import importlib.metadata
import re
import importlib
from typing import Union, Any, Optional
from pydantic import ValidationError


class Session:
    def __init__(self,
                 conf: Union[str, dict, list, tuple] = None,
                 log_level: str = None,
                 log_location: str = "",
                 log_maxlen: Optional[int] = 1e+5
                 ):
        """
        Initialise a session
        Parameters
        ----------
        conf: str, dict, list , tuple
            If a string is passed it must be either a path to a valid config file,
            or a valid config string in one of the supported format (e.g. JSON, YAML)
            If a dict is passed it will be used directly as the global conf and all the
            same principles apply as any other conf
            If a list or a tuple is passed this should be ???
        log_level: str
            The log level to use as per the standard logging package
            levels
        log_location: str
            Where to write log messages. This takes on of three arguments:
            "catalogue" will write to a catalogue object from where it will
            by accessible via the maeve.log object
            "stdout" will write to stdout
            "both" will write to both
        log_maxlen: int
            If logging to the catalogue, this will limit amount of events
            logged via a deque.
        """

        self.__version__ = importlib.metadata.version('maeve')

        log = Logger(
            log_level=log_level,
            log_maxlen=log_maxlen,
            log_location=log_location
        )

        self.g = Globals()  # package level immutables
        self.c = Catalogue(logger=log)  # the store of mutable shared objects and metadata
        self.r = Register()  # mutable shared variables e.g. recipes

        self.r._org = Confscade(conf, logger=log)
        # org level conf e.g. names, styles, colours etc.
        self.r.org = OrgConf(**self.r._org.get("org"))
        # env level conf e.g. locations
        self.r.env = EnvConf(**self.r._org.get("env"))

        self.log = self.c.add(
            log,
            name="session_log",
            metadata=dict(
                source=__name__,
                obj_type="maeve.util.Logger",
                description="The session log. Inspect object for methods for interrogating.",
            ),
            return_item="object",
        ).obj
        self.recipes = None
        self._get_recipes()

    def _get_recipes(self, loc: Union[str, list] = None):
        if not loc:
            if self.r.env.recipes_root:
                loc = self.r.env.recipes_root
            else:
                self.log.debug("No recipes locations found")
        loc = RecipeUtils.add_package_recipes(loc, self.r.env.load_package_recipes)
        self.recipes = Confscade(loc, env_conf=self.r.env, logger=self.log)
        self.r.recipes = self.recipes

    def router(func):
        def route(self, *args, **kwargs):
            if type(args[0]) is str and args[0] in self.g.core.cook_router_values:
                return func(self, self._router_params(*args, **kwargs), **kwargs.get("cook_kwargs", {}))
            if type(args[0]) is list:
                if kwargs.get("list_mode", "sequence"):
                    return self.cook_from_list(*args, **kwargs)
                else:
                    args[0] = self.recipe_list_to_pipeline(args[0])
                    return func(*args, *kwargs)
            return func(self, *args, **kwargs)
        return route


    @router
    def cook(self,
             recipe: Union[str, dict, list],
             obj: Any = None,
             overrides: dict = None,
             merge: dict = None,
             add_to_catalogue: bool = True,
             anchors: dict = None,
             catalogue_name: str = None,
             catalogue_metadata: dict = None,
             return_obj: bool = True,
             use_from_catalogue: bool = True,
             reload_recipes: bool = False,
             list_mode: str = "pipeline",
             *args,
             **kwargs
             ) -> Union[Any, None]:
        """
        Cooks (runs) a recipe and returns any results
        Parameters
        ----------
        recipe: str
            The name of recipe that exists in the recipes loaded
        obj: Any
            obj will be passed to plugin running the recipe, and depending on the recipe_type
            may or may not be acted upon. Use this to, for example, pass a DataFrame
            to a standalone function recipe or a pipeline.
        overrides: dict
            a dict with "path.to.item" : "newvalue" used to override specific values
        merge: dict
            a dict with a structure of the same type as the recipe which will be merged
            over the top based on the usual rules. Use this for more extensiove run time adjustments
            to recipes. This will be applied after inheritence, anchors and overrides have been resolved.
            This will be ignored if the recipe is a dict.
        add_to_catalogue: bool
            If True any objects returned as a result of cooking will be added to the catalogue
            Will be overridden by the synonymous flag in a recipe if present
        anchors: dict
            If anchors are present in the recipe being cooked which are keys in this dict
            then the corresponding value will replace the anchor. Where the same recipe name
            exists both in this dict and in the current recipe book, those in this dict
            will take precedence.
        catalogue_name: str
            The name to use when adding resulting object to catalogue
        catalogue_metadata: dict
            If the return object is being saved to the catalogue, then this dict
            will be used for that object's metadata.
        return_obj: bool
            If True, the object created by cooking will be returned. Beware, that if
            this is set to false, and `add_to_catalogue` is also False, then the object
            will be lost. This is not an error since not all recipes will yield and object
        use_from_catalogue: bool
            If True, then cook will check the catalogue for objects with the same
            name exist in the catalogue, and if so will return that. This can be helpful
            when working with, for example, large base datasets that can be cached and used
            by multiple dependant recipes. Beware: since catalogue items
            are mutable, the object returned may not be exactly as you expect.
            Setting this ,
            Default True.
        reload_recipes: bool
            if True will reload the entire recipe book before cooking. This is useful
            if you're making changes to the stored recipes.
        *args, **kwargs:
            Any additional args and kwargs will be passed directly to the
            plugin method being run. See docs for plugin for details
        Returns
        -------
            Any objects returned by cooking the recipe

        """
        _obj = obj

        # if we've not been passed an obj, and no adjustments are made to the recipe
        # then the recipe was run "as is". We will save this object in the catalogue
        # with an unmangled hash so that it can be safely reused.
        if obj is None and anchors is None and overrides is None:
            canonical = True
        else:
            canonical = False


        if reload_recipes:
            self._get_recipes()

        if type(recipe) is str:
            recipe_name = recipe
            recipe = self.recipes.get(recipe, anchors=anchors, overrides=overrides, exceptonmissing=True)
        elif type(recipe) is dict:
            recipe_name = None
        else:
            raise ValueError("recipe must be either str or dict")


        # use what's already in catalogue
        if use_from_catalogue and obj is None:
            try:
                self.log.debug("Attempting to retrieve from catalogue via recipe_hash")
                _obj = self.c.get(recipe, method="obj")
                self.log.info("Found recipe in catalogue so using that")
                return _obj
            except ValueError:
                self.log.debug("hashed recipe not in catalogue")
                pass

        if merge and type(merge) is dict:
            recipe = DictUtils.mergedicts(recipe, merge)
        add_to_catalogue = recipe.get("add_to_catalogue", add_to_catalogue)

        if recipe.get("add_to_catalogue", add_to_catalogue):
            if recipe.get("catalogue_name", catalogue_name):
                recipe_name = recipe["catalogue_name"]
                add_to_catalogue = True
        else:
            recipe_name = catalogue_name if catalogue_name else recipe_name


        try:
            plugin = recipe[self.g.conf.type_field]
        except KeyError:
            # attempts to identify recipe by using model validation
            # will raise if validates
            plugin = ModelInfo.identify_model(recipe, log=self.log)

        params = recipe.get(self.g.conf.init_params_field, {})
        name, method = self.parse_plugin_name(plugin)
        mod = self.init_plugin(name, params)
        obj = self.run_plugin(mod, recipe, method=method, obj=obj, *args, **kwargs)
        if obj is not None:
            if add_to_catalogue:
                cm = catalogue_metadata if catalogue_metadata else {"metadata": {}}
                if canonical:
                    cm["hash_recipe_with_obj"] = False
                else:
                    cm["hash_recipe_with_obj"] = True

                cm["name"] = cm.get("name", recipe_name)
                cm["recipe"] = recipe
                cm["metadata"]["source"] = cm.get("source", plugin)
                cm["metadata"]["obj_type"] = cm.get("obj_type", str(type(obj)))

                self.c.add(obj, **cm)

            if return_obj:
                return obj

    def init_plugin(
            self,
            plugin: Union[str, list],
            params: dict = None
    ):
        params = params if params else {}
        params = PluginParams(**params)
        return self.find_plugin(plugin)(self, *params.class_args, **params.class_kwargs)

    def run_plugin(self, mod, recipe, method: str = None, *args, **kwargs):
        if not method:
            method = self.g.conf.plugin_default_entrypoint
        return getattr(mod, method)(recipe, *args, **kwargs)

    def parse_plugin_name(self, name):
        parts = re.split(self.g.conf.plugin_delim, name)
        try:
            return parts[0], parts[1]
        except IndexError:
            return parts[0], None

    def find_plugin(self, plugin: Union[str, list, tuple]):
        if type(plugin) is str:
            bundled_plugin, cls = Plugins.resolve_plugin(plugin)
            if bundled_plugin:
                # see if it's a bundled plugin
                self.log.debug(f"Found bundled plugin {bundled_plugin} attempting to import via {__name__}")
                mod = importlib.import_module(bundled_plugin)
                return getattr(mod, cls)
            else:
                try:
                    # otherwise try and import from system
                    self.log.debug(f"Attempting to fetch 3rd party plugin {plugin}")
                    mod = importlib.import_module(plugin)
                except ModuleNotFoundError:
                    # give up
                    raise ValueError(f"No plugin found with name {plugin}")
                return getattr(mod, plugin)
        else:
            raise TypeError(f"Invalid type {type(plugin)} passed for plugin")

    def cook_from_list(self, recipes, *args, **kwargs):
        objs = []
        for r in recipes:
            try:
                obj = self.cook(r, *args, **kwargs)
                if obj is not None:
                    objs.append(obj)
            except (KeyError, ValueError) as e:
                self.log.warning(f"Recipe in list failed with error {e}")
        return objs

    def recipe_list_to_pipeline(self, recipes):
        return {
            "recipe_type": "pipeline",
            "pipeline": recipes
        }

    ########################################
    # Shortcuts
    ########################################

    # Data Loaders ####################

    def _router_params(self, *args, **kwargs):

        if args[0] in ["read_csv", "read_Excel"]:
            if len(args) == 2:
                kwargs["location"] = args[1]
            kwargs["convert_to_func"] = False
            return DataLoaderRecipe(function=args[0], **kwargs).model_dump()
        else:
            return {}

