from maeve.models.core import Globals

class Plugins:
    g = Globals()
    __plugin_alias = {
        "data": "Data",
        "Data": "Data",
        "list": "Primitives",
        "dict": "Primitives"
    }

    __plugin_map = {
        "Data": (f"{g.core.package_name}.plugins.data.core", "Data"),
        "Primitives": (f"{g.core.package_name}.plugins.primitives", "Primitives")
    }

    @classmethod
    def resolve_plugin(cls, plugin):
        return cls.__plugin_map.get(cls.__plugin_alias.get(plugin, None), (None, None))

