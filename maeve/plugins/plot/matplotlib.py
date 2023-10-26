from maeve.models.plot import MplGetSubplotsModel
import matplotlib.pyplot as plt
import matplotlib.projections as proj
import numpy as np
from typing import Union, Literal, Sequence, Any

class MplPlot:
    def __init__(self, session):
        self.s = session

    def subplots_recipe(self, recipe: dict, obj: Any = None) -> tuple:
        recipe = MplGetSubplotsModel(**recipe).model_dump()
        # handle if passed a data recipe
        # pass obj down into ax?
        return self.subplots(**recipe)

    main = subplots_recipe


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

    # custom ax functions go here


proj.register_projection(MPlotProjection)
