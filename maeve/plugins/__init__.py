

class Plugins:

    __plugin_alias = {
        "data": "Data",
        "Data": "Data"
    }

    __plugin_map = {
        "Data": "codename.plugins.data"
    }

    @classmethod
    def resolve_plugin(cls, plugin):
        return cls.__plugin_map.get(cls.__plugin_alias.get(plugin, None), None)

