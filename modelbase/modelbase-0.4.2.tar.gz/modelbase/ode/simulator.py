import numpy as _np
import matplotlib.pyplot as _plt
from mpl_toolkits.mplot3d import Axes3D as _Axes3D
import pandas as _pd
import re
import itertools
import concurrent.futures
import sys
import warnings
import json
import pickle
import scipy.integrate


# try to load assimulo, otherwise use scipy solvers
try:
    from assimulo.solvers import CVode
    from assimulo.problem import Explicit_Problem

    class _IntegratorAssimulo:
        def __init__(
            self,
            rhs,
            y0,
            verbosity,
            atol,
            rtol,
            max_error_failures,
            max_convergence_failures,
        ):
            self.problem = Explicit_Problem(rhs, y0)
            self.integrator = CVode(self.problem)
            self.integrator.atol = atol
            self.integrator.rtol = rtol
            self.integrator.maxnef = max_error_failures  # assimulo default 10
            self.integrator.maxncf = max_convergence_failures  # assimulo default 7
            self.integrator.verbosity = verbosity

        def simulate(self, t_end=None, steps=0, time_points=None):
            return self.integrator.simulate(t_end, steps, time_points)

        def simulate_to_steady_state(self, tolerance, **kwargs):
            """Simulation until numerical approximated steady state."""
            if "max_rounds" in kwargs:
                max_rounds = kwargs["max_rounds"]
            else:
                max_rounds = 3
            self.reset()
            t_end = 1000
            for n_round in range(1, max_rounds + 1):
                t, y = self.integrator.simulate(t_end)
                if _np.linalg.norm(y[-1] - y[-2], ord=2) < tolerance:
                    return y[-1]
                else:
                    t_end *= 1000
            raise ValueError("Could not find a steady state")

        def reset(self):
            self.integrator.reset()

    ASSIMULO_SUPPORT_FLAG = True

except ImportError:
    ASSIMULO_SUPPORT_FLAG = False


class _IntegratorScipy:
    def __init__(
        self,
        rhs,
        y0,
        verbosity,
        atol,
        rtol,
        max_error_failures,
        max_convergence_failures,
    ):
        self.rhs = rhs
        self.t0 = 0
        self.y0 = y0
        self.y0_orig = y0
        self.atol = atol
        self.rtol = rtol

    def simulate(self, t_end, steps=0, time_points=None):
        """Simulates the models. You have to supply either just the last time steps, or can add a number
        of return steps or give an array of the exact return time points.

        Parameters
        ----------
        t_end : float
            Last time step of the integration
        steps : int, optional
            Number of steps to return
        time_points : np.ndarray, optional
            Exact return points
        """
        if not steps == 0:
            # Scipy counts the total amount of return points rather than
            # steps as assimulo
            steps += 1
            t = _np.linspace(self.t0, t_end, steps)
        elif time_points is not None:
            t = time_points
        else:
            t = _np.linspace(self.t0, t_end, 100)
        y = scipy.integrate.odeint(self.rhs, self.y0, t, tfirst=True)
        self.t0 = t[-1]
        self.y0 = y[-1, :]
        return t, y

    def simulate_to_steady_state(self, tolerance, **kwargs):
        """Simulates the model to steady state

        Paramters
        ---------
        tolerance : float
            Maximum difference between two time steps after which a steady state is assumed
        """
        if "step_size" in kwargs:
            step_size = kwargs["step_size"]
        else:
            step_size = 1
        if "max_steps" in kwargs:
            max_steps = kwargs["max_steps"]
        else:
            max_steps = 100000
        if "integrator" in kwargs:
            integrator = kwargs["integrator"]
        else:
            integrator = "lsoda"
        self.reset()
        integ = scipy.integrate.ode(self.rhs)
        integ.set_integrator(integrator)
        integ.set_initial_value(self.y0)
        t = self.t0 + step_size
        y0 = self.y0
        for step in range(max_steps):
            y = integ.integrate(t)
            if _np.linalg.norm(y - y0, ord=2) < tolerance:
                return y
            else:
                y0 = y
                t += step_size
        raise ValueError("Could not find a steady state")

    def reset(self):
        self.t0 = 0
        self.y0 = self.y0_orig.copy()


class _Simulate:
    def __init__(self, model, integrator, verbosity):
        self._model = model
        self._t = None
        self._y = None
        self._time = []
        self._results = {}
        self._verbosity = verbosity
        self._integrator = integrator

        if not ASSIMULO_SUPPORT_FLAG:
            warnings.warn("Assimulo not found, disabling sundials support.")

    def clear_results(self):
        """Clears any previous simulations"""
        self._t = None
        self._y = None
        self._results = {}
        self.integrator.reset()

    def store_results_to_file(self, filename, format="json"):
        """Stores integration results in pickle file

        Parameters
        ----------
        filename : str
            Name of the pickle file
        format: str
            json or pickle

        Returns
        -------
        None
        """
        if format == "json":
            with open(filename, "w") as f:
                res = self.get_results("dict")
                for k, v in res.items():
                    res[k] = v.tolist()
                json.dump(res, f)
        elif format == "pickle":
            with open(filename, "wb") as f:
                pickle.dump(self.get_results("dict"), f)
        else:
            raise ValueError("Can only save to json or pickle")

    def load_results_from_file(self, filename, filetype="json"):
        """Loads integration results from a pickle file

        Parameters
        ----------
        filename : str
            Name of the pickle file
        format: str
            json or pickle

        Returns
        -------
        None
        """
        if filetype == "json":
            res = json.load(open(filename, "r"))
            self._time = _np.array(res["time"])
            res.pop("time")
            for k, v in res:
                self._results[k] = _np.array(v)
        elif filetype == "pickle":
            res = json.load(open(filename, "rb"))
            self._time = res["time"]
            res.pop("time")
            self._results = res
        else:
            raise ValueError("Can only save to json or pickle")

    def set_initial_conditions(
        self, y0, atol=1e-8, rtol=1e-8, max_error_failures=4, max_convergence_failures=1
    ):
        """Sets inital concentration vector

        Parameters
        ----------
        y0 : dict
            Initial concentrations
        """
        # Check if a simulation had run befor, if yes, reset the integrator
        if self._t is not None:
            self.clear_results()
        if isinstance(y0, dict):
            self._y0 = [y0[compound] for compound in self._model._compounds]
        elif (
            isinstance(y0, list) or isinstance(y0, _np.ndarray) or isinstance(y0, tuple)
        ):
            self._y0 = y0
        else:
            raise TypeError("Use dict, list or tuple for y0")
        self._model._stoichiometries_by_compounds = self._model.get_stoichiometries(
            "Compounds"
        )
        if self._integrator == "assimulo" and ASSIMULO_SUPPORT_FLAG:
            self.integrator = _IntegratorAssimulo(
                self._model._get_rhs,
                self._y0,
                self._verbosity,
                atol,
                rtol,
                max_error_failures,
                max_convergence_failures,
            )
        elif self._integrator == "scipy" or ASSIMULO_SUPPORT_FLAG is False:
            self.integrator = _IntegratorScipy(
                self._model._get_rhs,
                self._y0,
                self._verbosity,
                atol,
                rtol,
                max_error_failures,
                max_convergence_failures,
            )
        else:
            raise NotImplementedError("Only assimulo and scipy are supported")

        # Do a dry run to catch model construction errors beforehand
        fcd = self._model.get_full_concentration_dict(
            dict(zip(self._model.get_compounds(), self._y0))
        )
        self._model.get_fluxes(0, fcd)
        self._model.get_right_hand_side(0, self._y0)

    def simulate(self, t_end=None, steps=None, time_points=None):
        """Simulates the model. You can supply an end point, the
        amount of return steps or an array of the return points.

        Parameters
        ----------
        t_end : int or float
            Time end point
        steps : int
            Number of time steps
        time_points : list or nump.array
            Return points
        """
        if not hasattr(self, "_y0"):
            raise AttributeError(
                "No initial conditions set. Run set_initial_conditions method first."
            )
        if steps is not None and time_points is not None:
            warnings.warn(
                """
            You can either specify the steps or the time return points.
            I will use the time return points"""
            )
            t, y = self.integrator.simulate(t_end, 0, time_points)
        elif time_points is not None and steps is None:
            t, y = self.integrator.simulate(time_points[-1], 0, time_points)
        elif steps is not None and time_points is None:
            t, y = self.integrator.simulate(t_end, steps)
        else:
            t, y = self.integrator.simulate(t_end)

        t = _np.array(t)
        # Continuous simulation
        if self._t is None:
            self._t = t
            self._y = y
        else:
            self._t = _np.append(self._t, t[1:], axis=0)
            self._y = _np.append(self._y, y[1:, :], axis=0)
        self._time = _np.array(self._t)
        self._results = self._model.get_full_concentration_dict(
            dict(zip(self._model._compounds, self._y.T))
        )
        return _np.array(t), y.T

    def simulate_to_steady_state(self, tolerance=1e-6, **kwargs):
        """Simulation until numerical approximated steady state
        kwargs:
            assimulo:
                max_rounds: How often t_end is multiplied by 1000; default 3
            scipy:
                max_steps: maximal amount of steps of size step_size; default 1000
                step_size: integrator step size; default 1
                integrator: choose one of zvode, lsoda, dopri5 amd dop853; default lsoda
        """
        return self.integrator.simulate_to_steady_state(tolerance, **kwargs)

    def get_time(self):
        """Returns the time vector of the simulation(s)"""
        return self._time

    def get_y(self):
        """Returns the simulation results without the time"""
        return _np.array(list(self._results.values()))

    def get_results(self):
        """ Get simulation results"""
        return self._time, _np.array(list(self._results.values()))

    def get_results_dict(self):
        """ Get simulation results as dictionary"""
        results = {"time": self._time}
        results.update(self._results)
        return results

    def get_results_df(self):
        """ Get simulation results as dataframe"""
        return _pd.DataFrame(
            list(self._results.values()), self._results.keys(), self._time
        ).T

    def get_variable(self, variable_name, time_start=0, time_end=None):
        """Returns the integration values for a given variable and time span

        Parameters
        ----------
        variable_name : str
        time_start : int, optional
            Start index
        time_end : int, optional
            End index

        Returns
        -------
        numpy.ndarray
        """
        return self.get_results_dict()[variable_name][time_start:time_end]

    def get_variables(self, variable_list, time_start=0, time_end=None):
        """Returns the integration values for a list of given variables and time span

        Parameters
        ----------
        variable_list : list[str]
        time_start : int, optional
            Start index
        time_end : int, optional
            End index

        Returns
        -------
        numpy.ndarray
        """
        results = self.get_results_dict()
        return [results[i][time_start:time_end] for i in variable_list]

    def get_variables_dict(self, variable_list, time_start=0, time_end=None):
        """Returns the integration values for a list of given variables and time span

        Parameters
        ----------
        variable_list : list[str]
        time_start : int, optional
            Start index
        time_end : int, optional
            End index

        Returns
        -------
        results : dict
            Dictionary of the variables mapped to the respective values
        """
        results = self.get_results_dict()
        return {i: results[i][time_start:time_end] for i in variable_list}

    def get_variables_df(self, variable_list, time_start=0, time_end=None):
        """Returns the integration values for a list of given variables and time span

        Parameters
        ----------
        variable_list : list[str]
        time_start : int, optional
            Start index
        time_end : int, optional
            End index

        Returns
        -------
        results : pandas.DataFrame
            Dictionary of the variables mapped to the respective values
        """
        df = self.get_results_df()
        return df.loc[df.index[time_start:time_end], variable_list]

    def parameter_scan(self, parameter, parameter_range, t_end=100000):
        """Run simulations until a steady state for a given parameter pertubation is found.

        Parameters
        ----------
        parameter : str
            Name of the parameter
        parameter_range : list or numpy.array
            Range of values for which the parameter is varied
        t_end : int
            End time for the simulations

        """
        from . import Simulator

        # The function needs to be pickle-able. Sadly, this only works with a global variables
        global integrate
        global wrapper

        def wrapper(i):
            return integrate(i, self._model, parameter, self._y0)

        def integrate(i, model, parameter, y0):
            model.update_parameters({parameter: i})
            s = Simulator(model)
            s.set_initial_conditions(y0)
            s.integrator.maxncf = 1
            s.integrator.maxnef = 3
            try:
                s.simulate(t_end)
                return s.get_results()[1][:, -1]
            except:  # noqa: E722, assimulo does not give proper exceptions
                return _np.full(len(model.get_all_compounds()), _np.NaN)

        if sys.platform in ["win32", "cygwin"]:
            warnings.warn(
                """
            Windows does not behave well with multiple processes.
            Falling back to a single processing routine."""
            )
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = executor.map(wrapper, parameter_range)
        else:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = executor.map(wrapper, parameter_range)
        return _pd.DataFrame(
            results, index=parameter_range, columns=self._model.get_all_compounds()
        )

    def plot(
        self,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):
        """Plots all compounds, but not derived compounds

        Parameters
        ----------
        xlabel : str
        ylabel : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        legend_args : dict
            Arguments for placement of the legend
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        t = self._time
        for compound in self._model._compounds:
            ax.plot(t, self._results[compound])
        ax.legend(self._model._compounds, **legend_args)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_all(
        self,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):
        """Plots all compounds and derived compounds

        Parameters
        ----------
        xlabel : str
        ylabel : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        legend_args : dict
            Arguments for placement of the legend
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        t = self._time
        for compound in self._model._all_compounds:
            ax.plot(t, self._results[compound])
        ax.legend(self._model._all_compounds, **legend_args)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_selection(
        self,
        compound_list,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):
        """Plots a selection of compounds

        Parameters
        ----------
        xlabel : str
        ylabel : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        legend_args : dict
            Arguments for placement of the legend
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        t = self._time
        for compound in compound_list:
            ax.plot(t, self._results[compound], label=compound)
        ax.legend(**legend_args)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_grid(
        self,
        ncol,
        nrow,
        variable_groups,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(12, 6),
        titlesize=16,
        sharex=True,
        sharey=False,
    ):
        """Plots a selection of variables on a subplot grid

        Parameters
        ----------
        ncol : int
            Number of subplot columns
        nrow : int
            Number of subplot rows
        variable_groups : list[list[str]]
            Nested list of variable names
        xlabel : str
        ylabel : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        legend_args : dict
            Arguments for placement of the legend
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        fig, ax = _plt.subplots(
            ncol, nrow, figsize=figsize, sharex=sharex, sharey=sharey
        )
        ax = ax.ravel()

        for (n, plot), group in zip(enumerate(ax), variable_groups):
            for i in group:
                plot.plot(self._time, self._results[i], label=i)
            if n % 2 == 0:
                plot.set_ylabel(ylabel)
                plot.legend(
                    bbox_to_anchor=[-0.2, 1], loc="upper right", borderaxespad=0
                )
            else:
                plot.legend(bbox_to_anchor=[1.2, 1], loc="upper left", borderaxespad=0)
                if not sharey:
                    plot.set_ylabel(ylabel)
                    plot.yaxis.tick_right()
                    plot.yaxis.set_label_position("right")
        ax[-2].set_xlabel(xlabel)
        ax[-1].set_xlabel(xlabel)
        fig.suptitle(title, y=1.025, fontsize=titlesize)
        fig.tight_layout()
        return fig, ax

    def plot_against_variable(
        self,
        variable,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):
        """Plots all compounds against another system variable

        Parameters
        ----------
        variable : str
            Name of the variable
        xlabel : str
        ylabel : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        legend_args : dict
            Arguments for placement of the legend
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        ax.plot(self.get_variable(variable), self.get_y().T)
        ax.legend(self._model._compounds, **legend_args)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_fluxes(
        self,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):

        """Plots all fluxes

        Parameters
        ----------
        xlabel : str
        ylabel : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        legend_args : dict
            Arguments for placement of the legend
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        t = self._time
        fluxes = self._model.get_flux_array(t, self._y.T).T
        ax.plot(t, fluxes)
        ax.legend(self._model.get_rate_names(), **legend_args)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_fluxes_against_variable(
        self,
        variable,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):
        """Plots all fluxes against a chosen variable

        Parameters
        ----------
        variable : str
            Name of the variable
        xlabel : str
        ylabel : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        legend_args : dict
            Arguments for placement of the legend
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        t = self._time
        fluxes = self._model.get_flux_array(t, self._y.T).T
        ax.plot(self.get_variable(variable), fluxes)
        ax.legend(self._model.get_rate_names(), **legend_args)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_phase_plane(
        self, cpd1, cpd2, title="", figsize=(8, 6), titlesize=16, ax=None
    ):
        """Plots two variables against each other

        Parameters
        ----------
        cpd1 : str
        cpd2 : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()

        ax.plot(self._results[cpd1], self._results[cpd2])
        ax.set_xlabel(cpd1)
        ax.set_ylabel(cpd2)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_trajectories(self, cpd1, cpd2, y0, bounds, n, figsize=(8, 6), ax=None):
        """Plots trajectories of two compounds against each other

        Parameters
        ----------
        cpd1 : str
        cpd2 : str
        y0 : dict
            Initial conditions
        title : str
        figsize : tuple(int, int)
        titlesize : int
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()

        x = _np.linspace(*bounds[0], n)
        y = _np.linspace(*bounds[1], n)
        u = _np.zeros((n, n))
        v = _np.zeros((n, n))

        y_full = self._model.get_full_concentration_dict(y0)

        for i, s1 in enumerate(x):
            for j, s2 in enumerate(y):
                # Update y0 to new values
                y_full[cpd1] = s1
                y_full[cpd2] = s2
                # Possibly update algebraic modules as well
                y_full = self._model.get_full_concentration_dict(y_full)
                rhs = self._model.get_right_hand_side(0, y_full)
                u[i, j] = rhs[f"d{cpd1}dt"]
                v[i, j] = rhs[f"d{cpd2}dt"]

        ax.quiver(x, y, u.T, v.T)
        ax.set_xlabel(cpd1)
        ax.set_ylabel(cpd2)
        return fig, ax

    def plot_3d_phase_space(
        self,
        cpd1,
        cpd2,
        cpd3,
        title="",
        figsize=(8, 6),
        titlesize=16,
        ax=None,
        plot_kwargs={"lw": 0.5},
    ):
        """Plots three variables against each other

        Parameters
        ----------
        cpd1 : str
        cpd2 : str
        cpd3 : str
        title : str
        figsize : tuple(int, int)
        titlesize : int
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(
                1, 1, figsize=figsize, subplot_kw={"projection": "3d"}
            )
        else:
            fig = ax.get_figure()

        ax.plot(
            self._results[cpd1], self._results[cpd2], self._results[cpd3], **plot_kwargs
        )
        ax.set_xlabel(cpd1)
        ax.set_ylabel(cpd2)
        ax.set_zlabel(cpd3)
        ax.w_xaxis.pane.set_color("w")
        ax.w_yaxis.pane.set_color("w")
        ax.w_zaxis.pane.set_color("w")
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_3d_trajectories(
        self, cpd1, cpd2, cpd3, y0, bounds, n, figsize=(8, 6), ax=None
    ):
        """Plots the trajectories of three variables against each other

        Parameters
        ----------
        cpd1 : str
        cpd2 : str
        cpd3 : str
        y0 : dict
            Initial conditions
        title : str
        figsize : tuple(int, int)
        titlesize : int
        ax : matplotlib.pyplot.axes
            Axes on which to draw the plot

        Returns
        -------
        fig : matplotlib.pyplot.figure
        ax : matplotlib.pyplot.axes
        """
        if ax is None:
            fig, ax = _plt.subplots(
                1, 1, figsize=figsize, subplot_kw={"projection": "3d"}
            )
        else:
            fig = ax.get_figure()
        x = _np.linspace(*bounds[0], n)
        y = _np.linspace(*bounds[1], n)
        z = _np.linspace(*bounds[2], n)
        u = _np.zeros((n, n, n))
        v = _np.zeros((n, n, n))
        w = _np.zeros((n, n, n))

        y_full = self._model.get_full_concentration_dict(y0)

        for i, s1 in enumerate(x):
            for j, s2 in enumerate(y):
                for k, s3 in enumerate(y):
                    # Update y0 to new values
                    y_full[cpd1] = s1
                    y_full[cpd2] = s2
                    y_full[cpd3] = s3
                    # Possibly update algebraic modules as well
                    y_full = self._model.get_full_concentration_dict(y_full)
                    rhs = self._model.get_right_hand_side(0, y_full)
                    u[i, j, k] = rhs[f"d{cpd1}dt"]
                    v[i, j, k] = rhs[f"d{cpd2}dt"]
                    w[i, j, k] = rhs[f"d{cpd3}dt"]

        X, Y, Z = _np.meshgrid(x, y, z)
        ax.quiver(
            X,
            Y,
            Z,
            _np.transpose(u, [1, 0, 2]),
            _np.transpose(v, [1, 0, 2]),
            _np.transpose(w, [1, 0, 2]),
            length=0.05,
            normalize=True,
            alpha=0.5,
        )
        ax.set_xlabel(cpd1)
        ax.set_ylabel(cpd2)
        ax.set_zlabel(cpd3)
        return fig, ax


class _LabelSimulate(_Simulate):
    def __init__(self, model, integrator, verbosity):
        super().__init__(model, integrator, verbosity)

    def set_initial_conditions(
        self,
        init,
        label_position=None,
        atol=1e-8,
        rtol=1e-8,
        max_error_failures=4,
        max_convergence_failures=1,
    ):
        """Generate vector with initial concentrations of all compounds

        Parameters
        ----------
        y0 : dict
            Inital concentrations
        label_position : dict
            Specify which carbon position is labeled prior to the simulation
        """
        y0 = self._model._generate_y0(init, label_position)
        super().set_initial_conditions(
            y0, atol, rtol, max_error_failures, max_convergence_failures
        )

    def get_total_concentration(self, compound):
        """Returns the total concentration of a compound

        Parameters
        ----------
        compound : str
        """
        return self._results[compound + "_total"]

    def get_unlabled_concentration(self, compound):
        carbons = "0" * self._model.get_carbon_compounds(compound)
        return self.get_results_dict()[compound + f"_{carbons}"]

    def get_total_label_concentration(self, compound):
        """Returns the total concentration of of a compound that is labeled

        Parameters
        ----------
        compound : str
        """
        return self.get_results_dict()[compound + "_total"]

    def get_all_compound_variants(self, compound):
        """Returns the concentrations of all variants of a compound

        Parameters
        ----------
        compound : str
        """
        variants = self._model.get_compound_isotopomers(compound)
        return dict(zip(variants, [self._results[i] for i in variants]))

    def get_compounds_by_reg_exp(self, reg_exp):
        results = []
        for compound_name, v in self._results.items():
            if re.match(reg_exp, compound_name):
                results.append(v)
        return results

    def get_compound_dict_by_reg_exp(self, reg_exp):
        results = {}
        for compound_name, v in self._results.items():
            if re.match(reg_exp, compound_name):
                results[compound_name] = v
        return results

    def get_label_at_position(self, compound, position):
        """Returns the total concentration of a compound labeled at position n

        Parameters
        ----------
        compound : str
        position : int
            Position of the carbon label
        """
        carbons = self._model.get_carbon_compounds()[compound]
        label_positions = ["[01]"] * carbons
        label_positions[position] = "1"
        reg_exp = (
            "\A" + compound + "_" + "".join(label_positions) + "\Z"
        )  # noqa: W605, these escapes are ok
        return _np.sum(self.get_compounds_by_reg_exp(reg_exp), axis=0)

    def get_num_label(self, compound, number_of_labels):
        """Returns the total concentration of a compound with n labels.

        Parameters
        ----------
        compound : str
        number_of_labels : int
        """
        carbons = self._model.get_carbon_compounds()[compound]
        cpds = []
        for i in itertools.combinations(range(carbons), number_of_labels):
            lab = ["0"] * carbons
            for p in i:
                lab[p] = "1"
            cpds.append(self._results[compound + "_" + "".join(lab)])
        return _np.sum(cpds, axis=0)

    def get_total_rate(self, rate_name):
        """Retrieves the sum of all rates starting with rate_name"""
        raise NotImplementedError()

    def plot(
        self,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):
        """Plots total concentrations"""
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        t = self._time
        for compound, carbons in self._model.get_carbon_compounds().items():
            if carbons > 0:
                ax.plot(t, self._results[compound + "_total"])
            else:
                ax.plot(t, self._results[compound])
        ax.legend(self._model.get_carbon_compounds(), **legend_args)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_all(
        self,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        title="",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):
        """Plots all compounds and derived compounds"""
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        t = self._time
        all_compounds = set()
        for compound, carbons in self._model.get_carbon_compounds().items():
            if carbons > 0:
                ax.plot(t, self._results[compound + "_total"], label=compound)
                all_compounds.add(compound + "_total")
            else:
                ax.plot(t, self._results[compound], label=compound)
                all_compounds.add(compound)

        for compound in self._model._derived_compounds:
            if compound not in all_compounds:
                ax.plot(t, self._results[compound], label=compound)
        ax.legend(**legend_args)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=titlesize)
        return fig, ax

    def plot_label_distribution(
        self,
        compound,
        relative=False,
        xlabel="Remember to label your axis",
        ylabel="Remember to label your axis",
        figsize=(8, 6),
        titlesize=16,
        legend_args={
            "loc": "upper left",
            "bbox_to_anchor": (1.02, 1),
            "borderaxespad": 0,
        },
        ax=None,
    ):
        """Plots all label positions. If relative == True, the concentrations will be
        normalized to the total compound concentration

        Parameters
        ----------
        compound : str
            Compound which to plot
        relative : boolean
            If label concentrations should be normalized
        """
        if ax is None:
            fig, ax = _plt.subplots(1, 1, figsize=figsize)
        else:
            fig = ax.get_figure()
        carbons = self._model.get_carbon_compounds()[compound]
        if relative:
            total_concentration = self.get_total_concentration(compound)
            for i in range(carbons):
                ax.plot(
                    self._time,
                    self.get_label_at_position(compound, i) / total_concentration,
                    label="C{}".format(i + 1),
                )
            ax.set_ylabel("Relative Concentration")
        else:
            for i in range(carbons):
                ax.plot(
                    self._time,
                    self.get_label_at_position(compound, i),
                    label="C{}".format(i + 1),
                )
            ax.set_ylabel(ylabel)
        ax.legend(**legend_args)
        ax.set_xlabel(xlabel)
        ax.set_title(compound, fontsize=titlesize)
        return fig, ax

    def plot_multiple_label_distributions(
        self, compounds, relative=False, n_col=2, figure_width=16, cell_height=3
    ):
        """ Plots the label positions of all compounds in a grid.

        Parameters
        ----------
        compounds : list of str
            Compounds which to plot
        relative : boolean
            If label concentrations should be normalized
        n_col : int
            Number of columns in the plot grid
        figure_width : int or float
            Total width of the figure
        cell_height : int or float
            Height of each subplot
        """
        nrows = int(_np.ceil((len(compounds)) / n_col))
        fig, axs = _plt.subplots(
            nrows, n_col, figsize=[figure_width, cell_height * nrows]
        )
        for ax, (i, compound) in zip(axs.ravel(), enumerate(compounds)):
            carbons = self._model.get_carbon_compounds()[compound]
            total = self.get_total_concentration(compound)
            for i in range(carbons):
                conc = self.get_label_at_position(compound, i)
                if relative:
                    conc /= total
                ax.plot(self._time, conc, label="C{}".format(i + 1))
            if relative:
                ax.set_ylabel("Relative Concentration")
            else:
                ax.set_ylabel("Concentration")
            if i % 2 != 0:
                ax.legend(bbox_to_anchor=[-0.2, 1], loc="upper right", borderaxespad=0)
            else:
                ax.legend(bbox_to_anchor=[1.2, 1], loc="upper left", borderaxespad=0)
                ax.yaxis.set_label_position("right")
                ax.yaxis.tick_right()
            ax.ticklabel_format(axis="both", style="sci", scilimits=(-4, 4))
            ax.set_title(compound)
        fig.tight_layout()
        return fig, ax

    def plot_all_label_distributions(
        self, relative=False, n_col=2, figure_width=16, cell_height=3
    ):
        """ Plots the label positions of all compounds in a grid.

        Parameters
        ----------
        relative : boolean
            If label concentrations should be normalized
        n_col : int
            Number of columns in the plot grid
        figure_width : int or float
            Total width of the figure
        """

        # Exclude 0 carbon compounds
        compounds = {
            k: v for k, v in self._model.get_carbon_compounds().items() if v > 0
        }

        nrows = int(_np.ceil((len(compounds)) / n_col))
        fig, ax = _plt.subplots(
            nrows, n_col, figsize=[figure_width, cell_height * nrows]
        )
        ax = ax.ravel()
        if relative:
            for plot, (compound, carbons) in enumerate(compounds.items()):
                total = self.get_total_concentration(compound)
                for i in range(carbons):
                    ax[plot].plot(
                        self._time,
                        self.get_label_at_position(compound, i) / total,
                        label="C{}".format(i + 1),
                    )
                if plot % 2 == 0:
                    ax[plot].legend(
                        bbox_to_anchor=[-0.2, 1], loc="upper right", borderaxespad=0
                    )
                    ax[plot].set_ylabel("Relative Concentration")
                else:
                    ax[plot].legend(
                        bbox_to_anchor=[1.2, 1], loc="upper left", borderaxespad=0
                    )
                    ax[plot].set_ylabel("Relative Concentration")
                    ax[plot].yaxis.set_label_position("right")
                    ax[plot].yaxis.tick_right()
                ax[plot].set_title(compound)
        else:
            for plot, (compound, carbons) in enumerate(compounds.items()):
                for i in range(carbons):
                    ax[plot].plot(
                        self._time,
                        self.get_label_at_position(compound, i),
                        label="C{}".format(i + 1),
                    )
                if plot % 2 == 0:
                    ax[plot].legend(
                        bbox_to_anchor=[-0.2, 1], loc="upper right", borderaxespad=0
                    )
                else:
                    ax[plot].legend(
                        bbox_to_anchor=[1.2, 1], loc="upper left", borderaxespad=0
                    )
                    ax[plot].yaxis.tick_right()
                ax[plot].set_title(compound)
        fig.tight_layout()
        return fig, ax
