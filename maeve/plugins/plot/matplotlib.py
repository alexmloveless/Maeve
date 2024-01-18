from maeve.models.plot import MplSubplotsModel, MplPlotModel
from maeve.plugins.data.backends.polars import PolarsDataFrame, PolarsSeries
from maeve.plugins.data.backends.pandas import PandasUtils
from maeve.util.dict import DictUtils
import matplotlib.pyplot as plt
import matplotlib.projections as proj
import numpy as np
from typing import Any, Union
from matplotlib.dates import DateFormatter
from matplotlib import ticker
from matplotlib.dates import date2num, num2date
import pandas as pd
from itertools import zip_longest
from maeve.util.string import String


class Subplots:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax


class MplPlot:
    def __init__(self, session):
        self.s = session

    def main(self, recipe: dict, obj: Any = None) -> tuple:
        recipe = MplSubplotsModel(**recipe).model_dump()
        return self.subplots(**recipe)

    def mplot(self, recipe: dict, obj: Any = None) -> tuple:
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
            return self.subplots(**recipe["subplots_kwargs"])

    def subplots(self,
                 nrows: int = 1,
                 ncols: int = 1,
                 flattenax: bool = True,
                 rcparams: dict = None,
                 merge_rc: bool = True,
                 as_obj: bool = False,
                 subplots_kwargs: dict = None,
                 subplot_kw: dict = None
                 ) -> Union[Subplots, tuple]:
        mpl_conf = self.s.r.org.plugins.plot.get("matplotlib", {})
        base_rc = mpl_conf.get("rcparams", {})
        subplots_kwargs = subplots_kwargs if subplots_kwargs else {}
        subplot_kw = subplot_kw if subplot_kw else {}
        if rcparams:
            if merge_rc:
                rcparams = DictUtils.mergedicts(base_rc, rcparams)
        else:
            rcparams = base_rc

        with plt.rc_context(rcparams):
            fig, ax = plt.subplots(nrows, ncols, **subplots_kwargs, subplot_kw=subplot_kw)
            data = None
            if type(ax) is np.ndarray:
                axs = ax.flatten()
                for a in axs:
                    self.__augment_ax(a, data)
                if flattenax:
                    ax = axs
            else:
                self.__augment_ax(ax, data)

        if as_obj:
            return Subplots(fig, ax)
        else:
            return fig, ax

    def __augment_ax(self, ax, data):
        return ax

    ##############################################################################
    # Canned plots
    # These should be created in the following cases:
    #  - Wrappers around projection methods for standalone plots returning fig/ax
    #  - Plots with multiple parts (subplots)
    ##############################################################################

    def stackedbar(self, obj, subplots_kwargs=None, bar_kwargs=None):
        fig, ax = self.subplots(**subplots_kwargs)
        bar_kwargs = bar_kwargs if bar_kwargs else {}
        ax.stackedbar(obj, **bar_kwargs)
        return fig, ax


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

    def format_ticklabels(self, which='x', kind='int', date_format="number"):
        if which == 'x':
            axis = self.xaxis
        else:
            axis = self.yaxis

        if kind == 'date':
            axis.set_major_formatter(DateFormatter(date_format))
        else:
            axis.set_major_formatter(self.get_text_formatter(kind))

    def get_text_formatter(self, format):
        fmt = {
            "dollars": String.dollars_format,
            "$": String.dollars_format,
            "pounds": String.pounds_format,
            "£": String.pounds_format,
            "percent": ticker.PercentFormatter(),
            "%": ticker.PercentFormatter(),
            "perc": ticker.PercentFormatter(),
            "pct": ticker.PercentFormatter()
        }
        return fmt.get(format, String.number_format)

    def format_xticklabels(self, **kwargs):
        self.format_ticklabels(which="x", **kwargs)

    def format_yticklabels(self, **kwargs):
        self.format_ticklabels(which="y", **kwargs)

    def ts(self,
           data,
           kind="line",
           add_all_events=False,
           add_xmas=False,
           add_yearend=False,
           add_workdays=False,
           ylabeltype=None,
           xlabel_date_format=None,
           xlabeltype='date',
           grid=True,
           legend=True,
           labels=None,
           plot_kwargs=None,
           add_lines=None,
           add_trendline=None,
           trendline_fmt=None,
           mindate=None,
           maxdate=None,
           **kwargs
           ):
        """
        Create a timeseries

        Parameters
        ----------
        data: DataFrame, str, Series, dict, list like
            If a Dataframe - uses each column as a separate line. Uses the columns as line labels
            If a str will attempt to ingest and plot a Marty datasource
            If a Series - plots Series as a single line using Serines.index.name as the line label
            If list like will evaluate each line individually as a single line.
                - A tuple can be input as (label, (x, y)) where x and y are meaningful inputs to plt.plot()
                - A tuple can be input as (label, Series) where Series has a datetime index. The label will be used not the Series name
            if a dict it evals the same way as a list except using the dict key as the label and evaluating the value accordingly
        kind: str, default 'line'
            The type of chart to produce: line, bar, or stackedbar
        profile: str
            Override the default profile. Note: this will not affect the theme which can only be set via subplots
        add_all_events:
            Add vlines for all the standard events
        add_xmas: bool
            Add the vlines for xmas
        add_yearend: bool
            Add the vlines for year end
        add_workdays: bool
            Add the vlines for FY end
        ylabeltype: str
            Styles the ylabel values. Can be Int, Dollars or Pounds. Will automatically convert large ints to K/M
        xlabel_date_format: str
            If a valid date format string will apply that. Can also apply default named formats as defined in the profile (e.g. 'month', 'week')
        xlabeltype: str
            Defaults to 'date' but can also be set to 'int' e.g. if you've grouped by month number
        grid: bool
            Toggle the plot's grid
        legend: bool
            if True (default) will print whatever legend matplotlib can infer from the data.
        labels: str, list like
            By default, labels are implied from the data (e.g. from the column or series name).
            If a list label arg to each successive plot in the order of the list.
            If a string this will be applied to the first plot in the sequence only,
            all others will be inferred from the data.
            This method will always override the matplotlib label arg
            only falling back to it if no other options are available
        plot_kwargs: dict, list
            Each list item represents the kwargs for each of the plots line components and are fed in as **kwargs
            as each line is created. You can use this to change the line styling as per the usual matplotlib args
            (e.g. merker, linestyle etc.). For multi-line plots:
                - A single dict (not in a list) will be applied to all lines
                - A list the same length as the number of lines will be applied to each line in turn
                e.g. [{"marker":"o"}, None, {"linestle":"--"}] will apply styles to the first and thrid lines
                - A list of lesser length than the number of lines (including a list with a single dict)
                will apply each elemtn sequentially to the first n lines then apply None to all subsequent lines
        add_lines: list
            Given a list of tuples/lists with the form ([loc1, loc2 ...], {kwarg1: '', kwarg2: ''})
            will add single or sets of vlines styled accordingly
        add_trendline: bool
            Add a trendline to the data
        trendline_fmt: str
            Override the basic styling for the trendline

        Notes
        -----
        Colours will be applied as per the default cmap set in your session which uness you overrode it
        will be the default cmap (eycmap).
        """

        if PolarsSeries.is_polars_series(data) or PolarsDataFrame.is_polars_df(data):
            data = data.to_pandas()

        if type(data) in [pd.core.series.Series, pd.core.frame.DataFrame]:
            if type(data) is pd.core.frame.Series:
                data = data.to_frame()
            num_lines = data.shape[1]
            iter = data.items()
        elif type(data) is dict:
            iter = data.items()
            num_lines = len(data)
        else:
            iter = data
            num_lines = len(data)

        self.data = data

        if kind == "bar" or kind == "stackedbar":
            plotter = self.bar
        else:
            plotter = self.plot

        if not plot_kwargs or type(plot_kwargs) not in [list, tuple, dict]:
            plot_kwargs = [None] * num_lines
        elif type(plot_kwargs) is dict:
            plot_kwargs = [plot_kwargs] * num_lines

        llk = len(plot_kwargs)
        if llk < num_lines:
            plot_kwargs.extend([None] * (num_lines - llk))

        cols = []
        if labels:
            if type(labels) is str:
                labels = [labels]
            elif type(labels) in [list, tuple]:
                labels = labels
            else:
                self.log.warning(
                    f"`labels` arg must be either a str or list-like. got {type(labels)} so ignoring"
                )
                labels = []
        else:
            labels = []

        for i, kw, label in zip_longest(iter, plot_kwargs, labels):
            if not PandasUtils.dataframe_truth(i):
                continue
            _kwargs = kwargs.copy()
            _label = None
            if not kw:
                kw = {}
            if type(i) is tuple:
                _label = i[0]
                if type(i[1]) in [list, tuple]:
                    i = [i[1], i[2]]
                else:
                    # assume it's a Series
                    if kind == "bar" or kind == "stackedbar":
                        i = [i[1].index, i[1]]
                    else:
                        i = [i[1]]
            elif type(i) is pd.core.series.Series:
                _label = i.name
                if kind == "bar" or kind == "stackedbar":
                    i = [i.index, i]
                else:
                    i = [i]
            elif type(i) is pd.core.frame.DataFrame:
                if kind == "bar" or kind == "stackedbar":
                    d = i.iloc[:, 0]
                    _label = d.name
                    i = [d.index, d]
                elif i.shape[1] == 1:
                    _label = i.columns[0]
                    i = [i]
                else:
                    i = [i]
            else:
                self.log.warning("Unsupported data type for one of the plots: {}".format(type(i)))

            if label:
                _kwargs['label'] = label
            else:
                _kwargs['label'] = _label

            if kind == "stackedbar":
                if len(cols) == 0:
                    cols = i[1]
                else:
                    _kwargs['bottom'] = cols
                    cols = cols + i[1]

            _kwargs = {**_kwargs, **kw}
            plotter(*i, **_kwargs)

        if add_trendline:
            self.ts_add_tendline(fmt=trendline_fmt)

        self.format_ticklabels(which="y", kind=ylabeltype)
        if xlabeltype == "date":
            if xlabel_date_format:
                xlabel_date_format = self.interpret_date_str(xlabel_date_format)
            # else:
            #    xlabel_date_format = self.infer_date_freq(i.index.to_series())
        # self.format_ticklabels(which="x", kind=xlabeltype, date_format=xlabel_date_format)

        if legend:
            _ = self.legend()
        else:
            self.legend().remove()

        if grid:
            _ = self.grid(True)

        if add_all_events:
            self.ts_add_events(
                add_all=True,
                xmin=mindate,
                xmax=maxdate,
                add_lines=add_lines
            )
        else:
            self.ts_add_events(
                xmas=add_xmas,
                yearend=add_yearend,
                workdays=add_workdays,
                xmin=mindate,
                xmax=maxdate,
                add_lines=add_lines
            )

    def ts_add_tendline(self, fmt=None):
        from numpy.linalg import LinAlgError
        data = PandasUtils.df_to_series(self.data)
        x = date2num(data.index)
        try:
            z = np.polyfit(x, data, 1)
        except LinAlgError:
            self.log.warning("Unable to plot trendline due to LinAlgError. Check for NaNs in your data.")
            return
        p = np.poly1d(z)
        self.plot(data.index, p(x))

    def ts_add_events(self,
                      add_all=False,
                      xmas=True,
                      yearend=True,
                      workdays=None,
                      xmin=None,
                      xmax=None,
                      ymin=None,
                      ymax=None,
                      add_lines=None,
                      profile="ts",
                      theme=None
                      ):

        if add_all:
            xmas = yearend = workdays = True
        # Get data limits
        if type(xmin) is str:
            xmin = pd.to_datetime(xmin)
        if type(xmax) is str:
            xmax = pd.to_datetime(xmax)
        mints = xmin if xmin else num2date(self.dataLim.xmin)
        maxts = xmax if xmax else num2date(self.dataLim.xmax)
        minyear = mints.year
        maxyear = maxts.year
        ylims = self.get_ylim()
        ymin = ymin if ymin else ylims[0]
        ymax = ymax if ymax else ylims[1]

        # Xmas
        if xmas:
            xmases = [f'{x}-01-01' for x in np.arange(minyear + 1, maxyear + 1, 1)]
            self.vlines(xmases,
                        ymin=ymin, ymax=ymax,
                        # color=self.profile["ts_events"]["xmas"]["color"],
                        # linestyle=self.profile["ts_events"]["xmas"]["linestyle"],
                        # alpha=self.profile["ts_events"]["xmas"]["alpha"],
                        # linewidths=self.profile["ts_events"]["xmas"]["width"],
                        label='_nolegend_',
                        # **self.profile["ts_events"]["xmas"].get("kwargs", {})
                        )

        # year end
        if yearend:
            if mints.month > 6:
                yeminyear = minyear + 1
            else:
                yeminyear = minyear

            yrends = [f'{x}-07-01' for x in np.arange(yeminyear, maxyear + 1, 1)]
            self.vlines(yrends,
                        ymin=ymin, ymax=ymax,
                        # color=self.profile["ts_events"]["yearend"]["color"],
                        # linestyle=self.profile["ts_events"]["yearend"]["linestyle"],
                        # alpha=self.profile["ts_events"]["yearend"]["alpha"],
                        # linewidths=self.profile["ts_events"]["yearend"]["width"],
                        label='_nolegend_',
                        # **self.profile["ts_events"]["yearend"].get("kwargs", {})
                        )

        # holidays
        # if workdays not in [False, None]:
        #     if workdays is True:
        #         wd = self.get_workdays(mints, maxts)
        #         if wd is None:
        #             self.log.warning("No Marty data object available so cannot add workdays")
        #             return
        #     else:
        #         wd = self.get_workdays(mints, maxts, workdays=workdays, wddfcol='Workdays')
        #     self.vlines(wd,
        #                 ymin=ymin, ymax=ymax,
        #                 color=self.profile["ts_events"]["workdays"]["color"],
        #                 linestyle=self.profile["ts_events"]["workdays"]["linestyle"],
        #                 alpha=self.profile["ts_events"]["workdays"]["alpha"],
        #                 linewidths=self.profile["ts_events"]["workdays"]["width"],
        #                 label='_nolegend_',
        #                 **self.profile["ts_events"]["workdays"].get("kwargs", {})
        #                 )
        #
        if add_lines:
            for l in add_lines:
                if type(l[0]) not in [list, tuple]:
                    lines = [l[0]]
                else:
                    lines = l[0]
                self.vlines(lines, ymin=ymin, ymax=ymax, label='_nolegend_', **l[1])


proj.register_projection(MPlotProjection)
