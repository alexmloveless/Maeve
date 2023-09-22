from maeve.util import Logger
from maeve.plugins import Plugins
from maeve.models.core import Globals, OrgConf, EnvConf, PluginParams
from maeve.conf import Confscade
from maeve.catalogue import Catalogue, Register
from maeve.plugins.data.extensions import DataFrame

import re
import importlib
from typing import Union


class Session:
    def __init__(self,
                 conf: Union[str, dict, list, tuple] = None,
                 log_level: str = None
                 ):
        """
        Initialise a session
        Parameters
        ----------
        conf: str, dict, list , tuple
            If a string is passed it must be either a path to a valid config file,
            or a valid config string in one of the supported format (e.g. JSON, YAML)
            If a dict is passed it will be directly as the global conf and all the
            same principles apply as any other conf
            If a list or a tuple is passed this should be ???
        """

        self.g = Globals()  # package level immutables
        self.c = Catalogue()  # the store of mutable shared objects and metadata
        self.r = Register()  # mutable shared variables e.g. recipes

        self.r._org = Confscade(conf)
        self.r.org = OrgConf(**self.r.org.get("org"))
        self.r.env = EnvConf(**self.r.org.get("env"))

        self.log = Logger("main", self.r, log_level=log_level, log_maxlen=self.r.env.log_maxlen)
        self.r.recipes = self.get_recipes()


    def get_recipes(self, loc: Union[str, list] = None):
        if not loc:
            if self.r.env.recipes_loc:
                loc = self.r.env.recipes_loc
            else:
                self.log.debug(__name__, "No recipes locations found")
                return None
        return Confscade(loc)

    def cook(self,
             recipe,
             add_to_catalogue: bool = True,
             anchors: dict = None,
             catalogue_metadata: dict = None
             ):
        recipe = self.r.recipes.get(recipe, anchors=anchors)

        try:
            plugin = recipe[self.g.conf.type_field]
        except KeyError:
            raise ValueError(f"Cannot load a recipe without a '{self.g.conf.type_field} field'")

        params = recipe.get(self.g.conf.init_params_field, {})
        name, method = self.parse_plugin_name(plugin)
        mod = self.init_plugin(name, params)
        obj = self.run_plugin(mod, recipe, method=method)
        if add_to_catalogue:
            cm = catalogue_metadata
            cm["source"] = cm.get("source", plugin)
            cm["obj_type"] = cm.get("obj_type", type(obj))
            cm["name"] = cm.get("name", recipe)

            if anchors:
                cm["protect"] = "increment"
            else:
                cm["protect"] = "overwrite"

            self.c.add(obj, **cm)

    def init_plugin(
            self,
            plugin: Union[str, list],
            params: dict = None
    ):
        params = params if params else {}
        params = PluginParams(**params)
        return self.find_plugin(plugin)(self, *params.class_args, **params.class_kwargs)

    def run_plugin(self, mod, recipe, method: str = None):
        if not method:
            method = self.g.conf.plugin_default_entrypoint
        return getattr(mod, method)(self, recipe)

    def parse_plugin_name(self, name):
        parts = re.split(self.g.conf.plugin_delim, name)
        try:
            return parts[0], parts[1]
        except KeyError:
            return parts[0], None

    def find_plugin(self, plugin: Union[str, list, tuple]):
        if type(plugin) is str:
            bundled_plugin = Plugins.resolve_plugin(plugin)
            if bundled_plugin:
                # see if it's a bundled plugin
                self.log.debug(f"Found bundled plugin {bundled_plugin} attempting to import via {__name__}")
                mod = importlib.import_module(bundled_plugin)
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
        return mod
