import matplotlib.pyplot as plt
import matplotlib.projections as proj

class MPlot:
    def __init__(self, session):
        self.s = session

    def main(self, recipe):
        # handle routing here via dotted strings?
        pass

    def subplots(self, recipe, *args, **kwargs):
        return SubPlots(recipe, *args, **kwargs)

class SubPlots:
    def __init__(self):
        pass

    def subplots(self, recipe, figsize=(12, 6)):
        pass
        # if gridspec_kw:
        #     gs = Utils.mergedicts(profile.get("gridspec", {}), gridspec_kw)
        # else:
        #     gs = profile.get("gridspec", None)
        # sp = profile.get("subplots", None)
        # fig = profile.get("figure", None)
        # # theme = profile.get("theme", None)
        #
        # fig, ax = plt.subplots(rows, columns, gridspec_kw=gs, subplot_kw=sp, **fig, **kwargs)
        # if type(ax) is np.ndarray:
        #     axs = ax.flatten()
        #     for a in axs:
        #         self.__augment_ax(a, profile)
        #     if flattenax:
        #         ax = axs
        # else:
        #     self.__augment_ax(ax, profile)

class MPlotProjection(plt.Axes):
    name = "mplot"


proj.register_projection(MPlotProjection)
