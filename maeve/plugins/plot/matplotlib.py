from maeve.models.plot import MplSubplotsModel, MplPlotModel
import matplotlib.pyplot as plt
import matplotlib.projections as proj
import numpy as np
from typing import Any

class MplPlot:
    def __init__(self, session):
        self.s = session

    def subplots(self, recipe: dict, obj: Any = None) -> tuple:
        recipe = MplSubplotsModel(**recipe).model_dump()
        return self.subplots(**recipe)

    main = subplots

    def plot(self, recipe: dict, obj: Any = None) -> tuple:
        recipe = MplPlotModel(**recipe).model_dump()
        if recipe["plot_type"]:
            plot_type = recipe["plot_type"]
            if obj is None:
                if recipe["data_recipe"]:
                    obj = self.s.cook(recipe["data_recipe"])
                else:
                    raise ValueError("No data or data recipe found to plot")
            else:
                if type(obj) is str:
                    obj = self.s.cook(obj)

            return getattr(self, plot_type)(obj, subplots_kwargs=recipe["subplots_kwargs"], **recipe["plot_kwargs"])

        else:
            return self.subplots(**recipe)

    def stackedbar(self, obj, subplots_kwargs=None, bar_kwargs=None):
        fig, ax = self.subplots(**subplots_kwargs)
        bar_kwargs = bar_kwargs if bar_kwargs else {}
        ax.stackedbar(obj, **bar_kwargs)
        return fig, ax

    def subplots(self,
                 flattenax: bool = True,
                 rcparams: dict = None,
                 **kwargs
                 ) -> tuple:
        rcparams = rcparams if rcparams else {}
        with plt.rc_context(rcparams):
            fig, ax = plt.subplots(**kwargs)
            data = None
            if type(ax) is np.ndarray:
                axs = ax.flatten()
                for a in axs:
                    self.__augment_ax(a, data)
                if flattenax:
                    ax = axs
            else:
                self.__augment_ax(ax, data)

            return fig, ax

    def __augment_ax(self, ax, data):
        return ax


class MPlotProjection(plt.Axes):
    name = "mplot"

    def stackedbar(self, df, **kwargs):
        cols = []
        for c in df.iterrows():
            if len(cols) == 0:
                self.bar(c[1].index, c[1], label=c[0], **kwargs)
                cols = c[1]
            else:
                self.bar(c[1].index, c[1], bottom=cols, label=c[0], **kwargs)
                cols = cols + c[1]



proj.register_projection(MPlotProjection)
