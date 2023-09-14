from maeve.util import Util
from maeve.plugins import Plugins
from maeve.models.core import OrgConf, DataConf, RecipesConf
from maeve.plugins.data.extensions import DataFrame

from confscade import Confscade
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
        self.log = Util.get_logger(__name__, log_level)

        self.org = Confscade(conf)
        self.org_conf = OrgConf(**self.org.get("org"))
        self.data_conf = DataConf(**self.org.get("data"))
        self.recipes_conf = RecipesConf(**self.org.get("recipes"))
        self.load_recipes()

    def load_recipes(self):
        self.recipes = Confscade(self.recipes_conf.recipes_loc)

    def create(
            self,
            plugin: Union[str, list],
            *args,
            **kwargs
    ):
        mod = self.find_plugin(plugin)
        return mod(self, *args, **kwargs)

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

