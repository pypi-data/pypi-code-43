import collections
from copy import deepcopy
from logging import getLogger

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openscm.scmdataframe import ScmDataFrame
from openscm.scmdataframe.base import REQUIRED_COLS, ScmDataFrameBase
from scipy.interpolate import griddata

from scmcallib.finder.base import BaseFinder
from scmcallib.metrics import get_metric
from scmcallib.optimiser import get_optimiser
from scmcallib.plot import SummaryPlot
from scmcallib.utils import prepare_dataframe

logger = getLogger(__name__)


class EmulationResult(object):
    """Holds the results from emulating some predictor timeseries

    Contains the output coefficients and a number of plotting routines

    """

    def __init__(self, result, target, evaluator):
        # Check that the emulator converged
        assert result.success, "The emulator failed to converge: {}".format(
            result.message
        )

        self._result = result
        self.target = target
        self.parameter_set = evaluator.parameter_set
        self.samples = evaluator.samples
        self.scm_df = evaluator.scm_df

    def __len__(self):
        return len(self.samples)

    @property
    def coeffs(self):
        return self._result.x

    def plot_summary(self, fname=None, **kwargs):
        s = SummaryPlot(self.target, self.parameter_set)

        # Plot metric
        df = self.scm_df
        metric_vals = df[["run_num", "metric_value"]].drop_duplicates()
        s._ax_metric.scatter(
            metric_vals["run_num"], metric_vals["metric_value"], color="k", marker="x"
        )

        # plot params
        for p in s._ax_params:
            ax = s._ax_params[p]
            d = df[["run_num", p.lower()]]
            ax.scatter(d["run_num"], d[p.lower()], color="k", marker="x")

        # Queue up the timeseries
        for run_num in df["run_num"].drop_duplicates():
            ts = (
                df.filter(run_num=run_num)
                .timeseries(["run_num"] + self.target.columns.names)
                .T
            )

            s._timeseries.append(ts)
            if len(s._timeseries) > s.max_timeseries:
                s._timeseries = s._timeseries[-s.max_timeseries :]

        s.redraw_timeseries()
        s._write_summary(**df.meta.iloc[-1].to_dict())

        if fname is not None:
            s.save_fig(fname, **kwargs)

    def plot_fit(self, **plt_kwargs):
        nrows = len(self.target.columns)
        fig, axes = plt.subplots(nrows=nrows, **plt_kwargs)
        if nrows == 1:
            axes = [axes]

        for i, v in enumerate(self.target):
            filter = {k: val for k, val in zip(self.target.columns.names, v)}
            self.target[v].plot(ax=axes[i])
            self.fit.filter(**filter).timeseries().T.plot(
                ax=axes[i]
            )  # fit is a ScmDataFrame
            axes[i].set_title(v)
            axes[i].legend(["Obs", "Fit"])
        plt.tight_layout()
        return fig, axes

    def plot_heatmap(self, v1, v2, gridsize=15, **kwargs):
        self.samples.plot.hexbin(v1, v2, gridsize=gridsize, **kwargs)
        plt.gca().plot([self.coeffs[v1]], [self.coeffs[v2]], "rx")

    def plot_scatter(self, v1, v2, **kwargs):
        self.samples.plot.scatter(v1, v2, **kwargs)

    def plot_likelihood_surface(self, v1, v2, **kwargs):
        fig, ax = plt.subplots()
        x = self.samples[v1].astype(float)
        y = self.samples[v2].astype(float)

        metric_values = self.samples["metric_value"].astype(float).values.reshape(-1, 1)

        m = 200
        n = 200

        # define grid
        x_lin = np.linspace(x.min() * 1.2, x.max() * 0.9, m)
        y_lin = np.linspace(y.min() * 1.2, y.max() * 0.9, n)
        x_grid, y_grid = np.meshgrid(x_lin, y_lin)

        # grid the data
        z_grid = griddata(
            points=(x, y), values=metric_values, xi=(x_grid, y_grid), method="linear"
        )
        x_grid = x_grid.reshape(m, n)
        y_grid = y_grid.reshape(m, n)
        z_grid = z_grid.reshape(m, n)
        # contour the gridded data
        levels = np.logspace(0, 5, 20)

        plt.contour(
            x_grid, y_grid, z_grid, norm=matplotlib.colors.LogNorm(), levels=levels
        )

        plt.colorbar()  # draw colorbar
        # plot data points.
        ax.set_xlim(x_grid.min() * 1.2, x_grid.max() * 0.9)
        ax.set_ylim(y_grid.min() * 1.2, y_grid.max() * 0.9)
        ax.set_xlabel(v1)
        ax.set_ylabel(v2)

        ax.plot(x, y, "bo")
        ax.plot([self.coeffs[v1]], [self.coeffs[v2]], "rx")

    def _get_grid_bounds(x, y, x_trim, y_trim):

        x_range = x.max() - x.min()
        y_range = y.max() - y.min()

        x_min = x.min() + 0.5 * x_trim * x_range
        x_max = x.max() - 0.5 * x_trim * x_range

        y_min = y.min() + 0.5 * y_trim * y_range
        y_max = y.max() - 0.5 * y_trim * y_range

        return x_min, x_max, y_min, y_max

    @property
    def fit(self):
        # Assume that the last run is the final run
        run_idx = self.samples.iloc[-1].name
        return self.scm_df.filter(run_num=run_idx)

    def print_summary(self):
        print(self._result)


class Evaluator(object):
    def __init__(self, fitter, scm):
        self.fitter = fitter
        self.parameter_set = fitter.parameter_set
        self.parameter_names = fitter.parameter_set.names
        self.metric_func = fitter.metric_func
        self.scm = scm
        self.target = fitter.target

        # Storage for coefficients
        self._samples = collections.defaultdict(list)

        self._timeseries = []
        self.prev_fit = None

        self.live_plot = fitter.live_plot
        self.sample_step = fitter.sample_step
        if self.live_plot:
            self._summary_plot = SummaryPlot(self.target, self.parameter_set)

    def __call__(self, run_num=None, force_add=False, **run_parameters):
        """Runs the SCM with a given configuration and compare the results against the target data

        Parameters
        ----------
        run_num: int
            Optional value which uniquely identifies the run

        run_parameters: dict
            SCM parameters to run

        Returns
        -------
        float
            The metric_value calculated using self.metric_func
        """

        variables = list(self.target.columns.get_level_values("variable").unique())
        if self.fitter.iter_over_values is not None:
            all_cfg = []
            for v in self.fitter.iter_over_values:
                self.parameter_set.state = v
                all_cfg.append(
                    ({**run_parameters, **self.parameter_set.config_parameters}, v)
                )
            results = self.scm.run_multiple(all_cfg, variables=variables)
        else:
            results = self.scm.run(run_parameters, variables=variables)

        run_num = (
            run_num if run_num is not None else next(self.parameter_set.run_counter)
        )
        results = prepare_dataframe(results, self.fitter.iter_over)

        assert len(results), "Model returned no valid data"

        # Do the merging manually for now
        # results = self.scm.process_results(results)
        merged_idx = results.index.intersection(self.target.index)

        if len(merged_idx) == 0:
            raise ValueError("Output did not overlap with the target timeseries")
        ts = results.loc[merged_idx]
        ts -= ts.loc[slice(*self.fitter.reference_period)].mean()

        try:
            # We need to make sure that the ordering is correct. Both dfs are first use the same index which is the intersection of
            # the two indices. Then the columns from the target are extracted from the modelled timeseries (maintaining order).
            # A KeyError is raised if the modelled timeseries doesn't have a column specified in the target timeseries
            scm_ts = ts[self.target.columns].values.ravel()
            target_ts = self.target.loc[merged_idx].values.ravel()
            assert scm_ts.shape == target_ts.shape
            mask = np.isnan(scm_ts) | np.isnan(target_ts)

            if np.sum(~mask) == 0:
                raise ValueError("Could not find any overlapping non-nan values")

            weights = None
            if self.fitter.weights is not None:
                weights = self.fitter.weights.loc[merged_idx][
                    self.target.columns
                ].values.ravel()[~mask]

            metric_value = self.metric_func(
                scm_ts[~mask], target_ts[~mask], sample_weight=weights
            )
        except KeyError:
            logger.exception(
                "not all target data available. Have {}".format(ts.columns.to_list())
            )
            raise ValueError(
                "could not find overlapping scm time series for all of the training time series"
            )
        except ValueError:
            logger.warning(
                "Could not calculate metric value for run {}".format(run_num)
            )
            metric_value = np.nan

        to_save = run_parameters.copy()

        col_names = ts.columns.names
        ts = ts.T.reset_index()
        ts["run_num"] = run_num
        ts = ts.set_index(["run_num"] + col_names).T
        self.prev_fit = ts

        if force_add or (
            self.sample_step is not None and run_num % self.sample_step == 0
        ):
            to_save["metric_value"] = metric_value
            to_save["run_num"] = run_num
            self._timeseries.append(ts)
            for k in to_save:
                self._samples[k].append(to_save[k])

            if self.live_plot:
                self._summary_plot.add_sample(ts, **to_save)
                self._summary_plot.redraw_timeseries()

            logger.info("run_num: {} metric_value: {}".format(run_num, metric_value))
        return metric_value

    def run_multiple(self, df):
        """Takes a df and performs several runs

        Runs several runs of the scm calulating the metric_value on each iteration

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing the parameters to run. This can be easily obtained using `ParameterSet.evaluate`.

        Returns
        -------
        pd.DataFrame
            The ``df`` dataframe with an additional ``metric_value`` column


        See Also
        --------
        ``ParameterSet.evaluate``

        """
        res = [
            self(**coeffs.to_dict(), run_num=run_num)
            for run_num, coeffs in df.iterrows()
        ]
        df["metric_value"] = pd.Series(res, index=df.index)

        return df

    @property
    def samples(self):
        """Get a dataframe containing all of the sampled points during the life of the Evaluator

        Only create the DataFrame when needed as appending to a DF a row at a time is very slow

        Returns
        -------
        pd.DataFrame

        """
        d = self._samples.copy()
        if len(d["run_num"]) == 0:
            return pd.DataFrame()

        run_num = d.pop("run_num")
        df = pd.DataFrame(d, index=run_num)
        df.index.name = "run_num"
        return df

    @property
    def scm_df(self):
        """Get a dataframe containing all of the sampled points during the life of the Evaluator

        Only create the DataFrame when needed as appending to a DF a row at a time is very slow

        Returns
        -------
        openscm.dataframe.ScmDataFrame
        """

        if not len(self._timeseries):
            if self.prev_fit is None:
                return None
            self._timeseries = [self.prev_fit]

        from functools import reduce, partial

        outer_merge = partial(pd.merge, how="outer", left_index=True, right_index=True)
        df = reduce(outer_merge, self._timeseries)

        # merge in the extra metadata from the target timeseries
        if self.fitter.extra_meta is not None:
            meta_fields = self.fitter.extra_meta.index.names
            df = pd.merge(
                df.T.reset_index(),
                self.fitter.extra_meta.reset_index(),
                left_on=meta_fields,
                right_on=meta_fields,
            )
        else:
            df = df.T.reset_index()
        # Finally merge in the parameter values
        df = pd.merge(df, self.samples, left_on="run_num", right_index=True)
        df["climate_model"] = self.scm.name
        for f in REQUIRED_COLS:
            if f not in df:
                df[f] = "Unknown"
        df = ScmDataFrame(df)

        return df


class PointEstimateFinder(BaseFinder):
    """Generate a set of best-fit parameters which best emulate a given timeseries

    This class provides a wrapper to help emulate observational or model data to produce a single set of parameters.

    An example of setting up a model to calibrate MAGICC7 to global mean temperature observations

    .. code-block:: python

        emulator = PointEstimateFinder(param_set)
        emulator.set_target(observations)

        with MAGICC7_SCM() as scm:
            results = emulator.find_best_fit(scm)

    Parameters
    ----------
    parameter_set : scmcallib.parameterset.ParameterSet
        An instance of scmcallib.parameterset.ParameterSet which is used to define the constraints
        on the model. The config parameters will be updated to find the combination of parameters which best match the
        target data set using `set_target`.
    metric : str
        The metric used to calculate how well the modelled data matches the observations. This metric is
        the variable maximised in `find_best_fit`. Options include:

        - r_squared: R^2 value
        - explained_variance: Measure of the extent to which the modelled data accounts for the variation
        - neg_mean_sq_err: Mean square error (MSE)
        - neg_mean_abs_err: Mean absolute error (MAE)
        - neg_mean_sq_log_err: Mean square log error (MSLE)
        - neg_median_abs_err: Median absolute error (MedAE)
    sample_step : int or None
        Used to determine how often the parameter sets and fits are saved. ``sample_step`` is the step size between saving so for example
        a ``sample_step`` of 1 means that every sample is recorded while for a ``sample_step`` is 5 then every 5th sample is recorded.
        If ``sample_step`` is None then only the most recent sample is stored in the ``prev_fit`` attribute.
    live_plot : bool
        If True, than a summary plot is updated in realtime during the run. ``sample_step`` defines the frequency at which the figure
        is updated.
    kwargs :
        Additional options defined in ``BaseFinder``

    """

    def __init__(
        self,
        parameter_set,
        metric="neg_mean_sq_err",
        sample_step=1,
        live_plot=False,
        **kwargs,
    ):
        super(PointEstimateFinder, self).__init__(parameter_set, **kwargs)
        self.metric_name = metric
        self.metric_func = get_metric(metric)
        self._weights = None
        self.sample_step = sample_step
        self.live_plot = live_plot

    def _get_evaluator(self, scm):
        assert (
            self.target is not None
        ), "set_target must be called before the fit can be performed"

        return Evaluator(self, scm)

    def find_x0(self, scm, method="random", **kwargs):
        """Explore the parameter space to find a good starting point to begin optimisation

        This is only required for ``scipy`` optimiser. The ``bayesopt`` optimiser does not require initial conditions.

        Parameters
        ----------
        scm: ``scmcallib.scm.BaseSCM``
            SCM instance to run
        method : str
            The method for exploring the tune parameter space. Currently only randomly spampling the parameter space has been
            implemented. (Default value = 'random')
        kwargs :
            Optional parameters to pass to the sampling method

            - 'random`

                samples : int
                    The number of random samples to perform

        Returns
        -------
        dict:
            A best guess for the Tune Parameters
        """
        evaluator = self._get_evaluator(scm)
        if method == "random":
            results = evaluator.run_multiple(
                self.parameter_set.evaluate(kwargs.get("samples", 100))
            )
        else:
            raise ValueError("Unknown search method")

        self._initial_guesses = results

        # Find the value with the largest metric_value
        row = results.loc[results["metric_value"].dropna().idxmax()]

        tune_params = {k: row[k] for k in self.parameter_set.names}
        logger.info(
            "found x0: {} tune_params: {}".format(row["metric_value"], tune_params)
        )
        return tune_params

    def find_best_fit(self, scm, include_bounds=True, optimiser_name="scipy", **kwargs):
        """Find the optimal point given a starting point

        Parameters
        ----------
        scm: ``scmcallib.scm.BaseSCM``
            SCM instance to run
        include_bounds :
            If True, use hard bounds which limits the algorithm choices. Otherwise, values outside
            the bounds are not passed to the model, but result in a large penalty
        optimiser_name :
            The optimiser to use. Options are ['scipy', 'bayesopt']
             (Default value = "scipy")
        kwargs :
            Additional arguments to pass to the optimiser.

        Returns
        -------
        EmulationResult

        See Also
        --------
        OptimiserBayesOpt
        OptimiserScipy

        """
        logger.info("Beginning search for best fit")
        e = self._get_evaluator(scm)
        optimiser = get_optimiser(optimiser_name)()

        res = optimiser.find_best_fit(
            e, self.parameter_set, include_bounds=include_bounds, **kwargs
        )

        if res.success:
            # Run the best value one more time as the last value is assumed to be the fit
            m = e(**res.x, force_add=True)
            logger.info(
                "converged with a best fit of {} with a metric value of {}".format(
                    res.x, m
                )
            )

        return EmulationResult(res, self.target, e)

    def set_target(self, observed, iter_over=None, weights=None, **kwargs):
        """Specify the target timeseries

        During optimisation the SCM output will be compared to these data.

        The ScmDataFrame must contain unique combinations of variable and regions. Other metadata are ignored, except in the case
        where `iter_over` is specified. In that case `observed` must contain unique combinations of 'variable', 'region' and the
        columns which are being iterated over.

        Parameters
        ----------
        observed : ScmDataFrame or arraylike
            Observational/model data to which the SCM should be calibrated. This can be an ScmDataFrame or an arraylike.
            If using an arraylike object, additional ``kwargs`` may be needed.
        iter_over: str or list of str:
            Specify which metadata values to iterate over allowing for multiple model configurations to be run per optimiser step.
        weights: dict or openscm.scmdataframe.ScmDataFrame
            Relative weighting of the samples. See examples below for usage
        kwargs :
            Other options to convert an array to a ScmDataFrame. See ``create_iam_dataframe`` for available options.

        Examples
        --------

        If a dict of weights is provided, the keys are used to apply weights to variables. The ``filter`` syntax of ScmDataFrame is
        used so '*' can be used to specify many variables.

        >>> observed = ScmDataFrame(np.arange(20).reshape((10, 2)), columns={
            "index": range(2000, 2010),
            "model": ["a_iam"],
            "climate_model": ["a_model"],
            "scenario": ["a_scenario"],
            "region": ["World"],
            "variable": ["Surface Temperature", "SLR_EXPANSION"],
            "unit": ["K", "mm"],
        })
        >>> point_finder.set_target(observed, weights={
            'Surface Temperature': 10.
        })
        >>> point_finder.weights
        variable            Surface Temperature SLR_EXPANSION
        region                            World         World
        time
        2000-01-01 00:00:00                10.0           1.0
        2001-01-01 00:00:00                10.0           1.0
        2002-01-01 00:00:00                10.0           1.0
        2003-01-01 00:00:00                10.0           1.0
        2004-01-01 00:00:00                10.0           1.0
        2005-01-01 00:00:00                10.0           1.0
        2006-01-01 00:00:00                10.0           1.0
        2007-01-01 00:00:00                10.0           1.0
        2008-01-01 00:00:00                10.0           1.0
        2009-01-01 00:00:00                10.0           1.0


        Notes
        -----
        If overlapping variables are specified via dict weights, the order of operations can not be guaranteed

        """
        super(PointEstimateFinder, self).set_target(
            observed, iter_over=iter_over, **kwargs
        )

        if weights is None:
            return

        weights_df = deepcopy(observed)
        weights_df._data.loc[:, :] = 1.0  # TODO: add ScmDataFrame.set_data

        if isinstance(weights, ScmDataFrameBase):
            w = weights_df.timeseries()
            for idx, r in weights.timeseries().iterrows():
                w.loc[idx] = r
            weights_df = weights_df.__class__(w)  # Recreate an ScmDataFrame
        elif isinstance(weights, pd.Series):
            pass
        elif isinstance(weights, dict):
            for k in weights:
                v = np.atleast_2d(
                    weights[k]
                )  # This makes sure that v is of shape (1, n)
                idx = weights_df.filter(variable=k).meta.index
                if len(idx) == 0:
                    raise ValueError(
                        "Could not set weights for variable {}: no such variable".format(
                            k
                        )
                    )
                weights_df._data[idx] = v.T
        else:
            raise ValueError("Cannot handle weights of type {}".format(type(weights)))

        self._weights = prepare_dataframe(weights_df, self.iter_over)

    @property
    def weights(self):
        """Weights used to scale the target and scm timeseries

        The result contains a subset of meta columns

        The weights are set in ``PointEstimateFinder.set_target``

        Returns
        -------
        pd.DataFrame or None
        """
        return deepcopy(self._weights)
