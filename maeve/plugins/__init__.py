from maeve.models.core import Globals


class Plugins:
    g = Globals()
    __plugin_alias = {
        "list": "Primitives",
        "dict": "Primitives",
        "pipeline": "Pipeline",
        "function": "Function",
        "data_loader": "DataLoader",
        "dataloader": "DataLoader",
        "mpl_subplots": "MplSubPlot",
        "mpl_plot": "MplPlot"
    }

    __plugin_map = {
        "Primitives": (f"{g.core.package_name}.plugins.primitives", "Primitives"),
        "Pipeline": (f"{g.core.package_name}.plugins.core", "Pipeline"),
        "Function": (f"{g.core.package_name}.plugins.core", "Function"),
        "DataLoader": (f"{g.core.package_name}.plugins.data.extensions", "DataLoader"),
        "MplSubPlot": (f"{g.core.package_name}.plugins.plot.matplotlib", "MplPlot"),
        "MplPlot": (f"{g.core.package_name}.plugins.plot.matplotlib", "MplPlot.plot")
    }

    @classmethod
    def resolve_plugin(cls, plugin):
        return cls.__plugin_map.get(cls.__plugin_alias.get(plugin, None), (None, None))

