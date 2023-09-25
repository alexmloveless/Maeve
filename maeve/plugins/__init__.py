from maeve import Globals as g

class Plugins:

    __plugin_alias = {
        "data": "Data",
        "Data": "Data"
    }

    __plugin_map = {
        "Data": (f"{g.packagename}.plugins.data.core", "Data")
    }

    @classmethod
    def resolve_plugin(cls, plugin):
        return cls.__plugin_map.get(cls.__plugin_alias.get(plugin, None), (None, None))

