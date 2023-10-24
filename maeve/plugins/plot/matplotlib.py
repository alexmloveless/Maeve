import matplotlib.pyplot as plt

class MPlot:
    def __init__(self, session):
        self.s = session

    def main(self, recipe):
        # handle routing here via dotted strings?
        pass

    def subplots(self, *args, **kwargs):
        return SubPlots()

class SubPlots:
    def __init__(self):
        pass

    def subplots(self, recipe):
        pass
        # if profile:
        #     profile = self.get_profile(profile, theme=theme)
        # else:
        #     profile = copy.deepcopy(self.profile)
        #     if theme:
        #         MPlot.set_theme(theme)
        # if figsize:
        #     profile["figure"]["figsize"] = figsize
        #
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
