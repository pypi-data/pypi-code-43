import collections
from datetime import datetime

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler

summary_plot_text = """{}
Run Date: {}
{}
Config Parameters:
{}

Model-Specific Parameters:
{}

Tune Parameters:
{}
"""


class SummaryPlot(object):
    """

    Parameters
    ----------
    target : pd.DataFrame

    params_to_show : list of str
        A list of parameter names to plot
    """

    max_timeseries = 50

    def __init__(self, target, parameter_set):
        self.parameter_set = parameter_set
        self.params_to_show = parameter_set.tune_parameters
        self.target = target
        self._text = None
        self._initialise_plot()
        self._write_summary()
        self._timeseries = []

    def _write_summary(self, **kwargs):
        if self._text:
            self._text.remove()

        # Get a table of model specific parameters
        def _get_model_specific(r):
            self.parameter_set.state = r.to_dict()
            return pd.Series(self.parameter_set.model_specific_parameters)

        if len(self.target.columns.levels) > 2:
            meta_table = self.target.columns.droplevel(
                ("region", "variable")
            ).to_frame()
            model_specific_df = meta_table.apply(_get_model_specific, axis=1)
            model_specific_df = "" if model_specific_df.empty else model_specific_df
        else:
            model_specific_df = ""

        text = summary_plot_text.format(
            "",
            datetime.now().isoformat(),
            "Metric: {}".format(kwargs["metric_value"])
            if "metric_value" in kwargs
            else "",
            "\n".join(
                [
                    "{}: {}".format(k, v)
                    for k, v in self.parameter_set.config_parameters.items()
                ]
            ),
            model_specific_df,
            "\n".join(
                "{}: {}".format(
                    tune_param,
                    kwargs[tune_param.lower()] if tune_param.lower() in kwargs else "",
                )
                for tune_param in self.parameter_set.tune_parameters.keys()
            ),
        )

        self._text = self._fig.text(0.01, 0.02, text, fontsize="x-small")

    def _initialise_plot(self):
        plt.ion()
        nparams = len(self.params_to_show)
        regions = sorted(self.target.columns.get_level_values("region").unique())
        variables = sorted(self.target.columns.get_level_values("variable").unique())

        ncols = 2 + len(regions)  # (meta/GOF) | (params) | n * (region)
        nrows = max(max(nparams, len(variables)), 2)
        self._fig = plt.figure(figsize=(5 * ncols, 3 * nrows))
        gs = gridspec.GridSpec(nrows, ncols, figure=self._fig)

        self._ax_metric = plt.subplot(gs[0, 0])
        self._ax_metric.set_title("Metric Value", fontsize="x-small")

        self._ax_params = {}
        common_ax = None
        for i, param in enumerate(self.params_to_show):
            ax = plt.subplot(gs[i, 1], sharex=common_ax)
            ax.set_title(param, fontsize="x-small")
            self._ax_params[param] = ax
            if common_ax is None:
                common_ax = ax

        self._ax_variables = {}

        cc = cycler(color=["0.5", "0.3", "0.7"]) * cycler(
            linestyle=["-", "--", "-.", ":"],
            dashes=[(None, None), (10, 10), (10, 10), (10, 10)],
        )
        cc_iter = cc()
        self._meta_styles = collections.defaultdict(lambda: next(cc_iter))

        prop_cycle = plt.rcParams["axes.prop_cycle"]
        colors = cycler(color=prop_cycle.by_key()["color"])()
        self._meta_colours = collections.defaultdict(lambda: next(colors))

        # Setup the variable plots
        common_ax = None  # All thevariable axes share their x axis
        for col in self.target.columns:
            # index subplots by unique (variable, regions)
            idx = (col[0], col[1])
            if idx not in self._ax_variables:
                variable_idx = variables.index(col[0])
                region_idx = regions.index(col[1])

                ax = plt.subplot(gs[variable_idx, 2 + region_idx], sharex=common_ax)
                if common_ax is None:
                    common_ax = ax
                ax.set_title(idx, fontsize="x-small")
                self._ax_variables[idx] = ax

        #  Work out the bounds of the target variables
        #  The plots are then set up to span the range of the variable and a little bit extra
        self._ax_variable_bounds = {}
        t = self.target.groupby(level=["variable", "region"], axis=1).apply(
            lambda df: pd.Series(np.quantile(df.values, [0, 1.0]), index=[0, 1])
        )
        for idx in t.columns:
            tmax = t[idx][1]
            tmin = t[idx][0]
            mid = (tmax + tmin) / 2
            half_span = (tmax - tmin) / 2  #
            bounds = (mid - half_span * 1.2, tmax + half_span * 1.2)
            self._ax_variable_bounds[idx] = bounds
            self._ax_variables[idx].set_ylim(*bounds)
            if len(self.target.columns.levels) > 2:
                self._ax_variables[idx].legend(fontsize="xx-small")

        self._fig.tight_layout(h_pad=1.5, rect=(0, 0.03, 1, 0.97))
        self._fig.canvas.draw()
        plt.pause(0.01)

    def add_sample(self, fit, redraw=False, **params):
        """
        Add a sample to the summary plot

        Parameters
        ----------
        fit: pd.DataFrame
            The
        params : Tuning parameters, metrics and run number
        """
        params = {k.lower(): params[k] for k in params}
        run_num = params["run_num"]

        # Plot metric
        self._ax_metric.scatter(run_num, params["metric_value"], color="k", marker="x")

        # plot params
        for p in self._ax_params:
            ax = self._ax_params[p]
            ax.scatter(run_num, params[p.lower()], color="k", marker="x")

        self._timeseries.append(fit)
        if len(self._timeseries) > self.max_timeseries:
            self._timeseries = self._timeseries[-self.max_timeseries :]

        if redraw:
            self.redraw_timeseries()
        self._write_summary(**params)

    def redraw_timeseries(self):
        """
        Update the figure

        Operates in a non-blocking manner, i.e. program execution continues unlike ``plt.show``
        """
        # Clear the plots
        for idx in self._ax_variables:
            ax = self._ax_variables[idx]
            ax.clear()
            ax.set_title(idx)
            ax.set_ylim(*self._ax_variable_bounds[idx])

        def plot_fit(ts, style_dict, prefix=None, **styles):
            for col in ts.columns:
                idx = (col[1], col[2])  # col0 is now run_num
                if idx in self._ax_variables:
                    ax = self._ax_variables[idx]
                    name = col[3:] if len(col) > 3 else None
                    ts[col].plot(
                        ax=ax,
                        **styles,
                        **style_dict[name],
                        label="{}: {}".format(prefix, name) if prefix else "_nolegend_",
                    )

        plot_fit(self._timeseries[-1], self._meta_colours, prefix="Fit", linestyle="--")
        # Plot the old timeseries
        for ts in self._timeseries[:-1]:
            plot_fit(ts, self._meta_styles, linewidth=0.2)

        # plot the target
        for col in self.target.columns:
            idx = (col[0], col[1])
            if idx in self._ax_variables:
                ax = self._ax_variables[idx]
                name = col[2:] if len(col) > 2 else None
                self.target[col].plot(
                    ax=ax, **self._meta_colours[name], label="Target: {}".format(name)
                )
        for idx in self._ax_variables:
            ax = self._ax_variables[idx]
            ax.legend()

        self._fig.canvas.draw()
        plt.pause(0.001)  # needed to redraw the plot

    def save_fig(self, fname, **kwargs):
        """
        Save the figure to file

        Parameters
        ----------
        fname : str or file-like object
            A string containing a filepath or an open file object.
        kwargs
            Other optional arguments passed to matplotlib.figure.Figure.savefig

        """
        self._fig.savefig(fname, **kwargs)
