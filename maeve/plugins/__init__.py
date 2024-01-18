import importlib
from typing import Union
from maeve.models.core import Globals, PluginParams
import re


class Plugins:
    def __init__(self, session):
        self.s = session
        self.s.g = Globals()
        self.__plugin_alias = {
            "list": "Primitives",
            "dict": "Primitives",
            "pipeline": "Pipeline",
            "function": "Function",
            "data_loader": "DataLoader",
            "dataloader": "DataLoader",
            "mpl_subplots": "MplSubPlot",
            "mpl_plot": "MplPlot"
        }

        self.__plugin_map = {
            # plugin loc, Class, default method, method expects recipe
            "Primitives": (f"{self.s.g.core.package_name}.plugins.primitives", "Primitives", "main"),
            "Pipeline": (f"{self.s.g.core.package_name}.plugins.core", "Pipeline", "main"),
            "Function": (f"{self.s.g.core.package_name}.plugins.core", "Function", "main"),
            "DataLoader": (f"{self.s.g.core.package_name}.plugins.data.extensions", "DataLoader", "main"),
            "MplSubPlot": (f"{self.s.g.core.package_name}.plugins.plot.matplotlib", "MplPlot", "main"),
            "MplPlot": (f"{self.s.g.core.package_name}.plugins.plot.matplotlib", "MplPlot", "mplot")
        }

    def get_plugin(
            self,
            plugin,
            params=None,
            init=True
    ):
        name, req_method = self.parse_plugin_name(plugin)
        params = params if params else {}
        params = PluginParams(**params)
        cls, target_method = self.find_plugin(plugin)
        if all([req_method, target_method]):
            raise ValueError("Both recipe and plugin target contained a method request. Cannot resolve")
        method = target_method if target_method else req_method  # method defaults to None
        if not init:
            return cls, method
        else:
            mod = cls(self.s, *params.class_args, **params.class_kwargs)
            return mod, method

    def get_and_run_plugin(
            self,
            plugin,
            recipe=None,
            obj=None,
            params=None,
            method: str = None,
            *args, **kwargs
    ):
        mod, method_ = self.get_plugin(plugin, params)
        if not method:
            method = method_
        return self.run_plugin_method(mod, recipe=recipe, method=method, obj=obj, *args, **kwargs)

    run = get_and_run_plugin

    def resolve_plugin(self, plugin):
        return self.__plugin_map.get(self.__plugin_alias.get(plugin, None), (None, None, None))

    def run_plugin_method(self, mod, recipe=None, method: str = None, *args, **kwargs):
        if not method:
            method = self.s.g.conf.plugin_default_entrypoint
        if recipe:
            return getattr(mod, method)(recipe, *args, **kwargs)
        else:
            return getattr(mod, method)(*args, **kwargs)

    def parse_plugin_name(self, name):
        parts = re.split(self.s.g.conf.plugin_delim, name)
        try:
            return parts[0], parts[1]
        except IndexError:
            return parts[0], None

    def find_plugin(self, plugin: Union[str, list, tuple]):
        if type(plugin) is str:
            bundled_plugin, cls, method = self.resolve_plugin(plugin)
            if bundled_plugin:
                # see if it's a bundled plugin
                self.s.log.debug(f"Found bundled plugin {bundled_plugin} attempting to import via {__name__}")
                mod = importlib.import_module(bundled_plugin)
                return getattr(mod, cls), method
            else:
                try:
                    # otherwise try and import from system
                    self.s.log.debug(f"Attempting to fetch 3rd party plugin {plugin}")
                    mod = importlib.import_module(plugin)
                except ModuleNotFoundError:
                    # give up
                    raise ValueError(f"No plugin found with name {plugin}")
                return getattr(mod, plugin), None
        else:
            raise TypeError(f"Invalid type {type(plugin)} passed for plugin")
