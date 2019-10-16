# modelbase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# modelbase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with modelbase.  If not, see <http://www.gnu.org/licenses/>.

"""Model

Description of the module

"""

import numpy as np
import warnings
import pandas as pd
import inspect
from .. import core
from .. import io


class Model(core.ParameterModel):
    """The main class for modeling. Provides model construction and inspection tools."""

    def __init__(self, parameters=None):
        super().__init__(parameters)
        self._all_compounds = {}
        self._derived_compounds = {}
        self._rates = {}
        self._algebraic_modules = {}
        self._stoichiometries = {}
        self._stoichiometries_by_compounds = {}
        self._ratelaws = {}
        self._module_templates = {}

    def __str__(self):
        """Gives a string representation of the system of ODEs for the model"""

        rhs = """def rhs(t, y):\n"""
        # Unpack variables
        rhs += "    {} = y\n".format(",".join(self._compounds))

        # Create full concentration vector
        for mod in self._algebraic_modules.values():
            mod_func = mod["func"].__name__
            rhs += "    {} = {}(p, {})\n".format(
                ", ".join(mod["der_vars"]), mod_func, ", ".join(mod["vars"])
            )
        # Create equations
        for cpd, rates in self.get_stoichiometries("Compounds").items():
            rhs += "    d{}dt = ".format(cpd)
            for rate, factor in rates.items():
                rate_func = self._rates[rate]["func"].__name__
                var = ["p"]
                [var.append(i) for i in self._rates[rate]["vars"]]
                rhs += "({} * {}({})) + ".format(factor, rate_func, ", ".join(var))
            rhs = rhs[:-3]  # remove last " + "
            rhs += "\n"
        # Return
        rhs += "    return [{}]".format(
            ", ".join(["d" + i + "dt" for i in self._compounds])
        )
        return rhs

    def _collect_algebraic_module_functions(self):
        """Function needed for string representation of the model. Collects names, variables, derived
        variables and the function source code of every algebraic module."""
        algebraic_modules = {}
        for name, am_dict in self._algebraic_modules.items():
            function, variables, derived_variables = am_dict.values()
            function_str = inspect.getsource(function)[:-1]  # [:-1] removes line break
            if "lambda" in function_str:
                raise ValueError("lambda functions not supported")
            algebraic_modules[function.__name__] = function_str
        return algebraic_modules

    def _collect_rate_functions(self):
        """Function needed for string representation of the model. Collects names, variables and the
        function source code of every rate function."""
        rate_functions = {}
        for name, rate_dict in self._rates.items():
            function, variables = rate_dict.values()
            function_str = inspect.getsource(function)[:-1]  # Remove line break
            if "lambda" in function_str:
                raise ValueError("lambda functions not supported")
            rate_functions[function.__name__] = function_str
        return rate_functions

    def _generate_rate_functions_string(self):
        """Function needed for string representation of the model. Generates the string representation of the
        rate functions."""
        rate_functions_string = ""
        for name, rate_dict in self._rates.items():
            function, variables = rate_dict.values()
            rate_functions_string += f"m.add_reaction('{name}', "
            rate_functions_string += (
                f"{function.__name__}, {self._stoichiometries[name]}, {variables})"
            )
            rate_functions_string += "\n"
        return rate_functions_string

    def _generate_algebraic_modules_string(self):
        """Function needed for string representation of the model. Generates the string representation of the
        algebraic modules."""
        am_string = ""
        for name, am_dict in self._algebraic_modules.items():
            function, variables, derived_variables = am_dict.values()
            am_string += f"m.add_algebraic_module('{name}', "
            am_string += f"{function.__name__}, {variables}, {derived_variables})"
            am_string += "\n"
        return am_string

    def generate_model_source_code(self):
        """Generates the construction source code for the model. Useful for exporting the model in a standardized
        fashion"""
        model_string = ""
        model_string += "# Define algebraic module functions\n"
        for module in self._collect_algebraic_module_functions().values():
            model_string += module
            model_string += "\n\n"

        model_string += "# Define rate functions\n"
        for rate in self._collect_rate_functions().values():
            model_string += rate
            model_string += "\n\n"

        model_string += "# Define parameters\n"
        model_string += f"parameters = {self._parameters.__dict__}"
        model_string += "\n\n"

        model_string += "# Initiate model\n"
        model_string += f"m = Model(parameters)"
        model_string += "\n\n"

        model_string += "# Add compounds\n"
        model_string += f"m.add_compounds({list(self._compounds.keys())})"
        model_string += "\n\n"

        model_string += "# Add algebraic modules\n"
        model_string += f"{self._generate_algebraic_modules_string()}"
        model_string += "\n\n"
        model_string += "# Add rate functions\n"
        model_string += f"{self._generate_rate_functions_string()}"
        return model_string

    def write_to_sbml(self, filename=None):
        return io.sbml.write_to_sbml(self, filename)

    ##########################################################################
    # Compound function extensions
    ##########################################################################
    def _number_compounds(self):
        """Enumerates the compounds.
        First numerates the model compounds (super call), then adds the derived compounds from
        the algebraic modules. Stored in two different dictionaries: self._compounds and self._all_compounds.
        """
        super()._number_compounds()

        algebraic_compounds = []
        for v in self._algebraic_modules.values():
            for compound in v["der_vars"]:
                if compound not in algebraic_compounds:
                    algebraic_compounds.append(compound)

        self._all_compounds = {}
        self._all_compounds.update(self._compounds)

        for number, compound in enumerate(algebraic_compounds, len(self._compounds)):
            self._all_compounds[compound] = number
            self._derived_compounds[compound] = number

    def get_all_compounds(self):
        """Returns model compounds with derived compounds from
        algebraic modules.

        Returns
        all_compounds: dict
            Dictionary of all compounds and compounds derived from algebraic modules
        """
        return self._all_compounds

    ##########################################################################
    # Basic rate functions
    ##########################################################################
    def add_rate(self, rate_name, rate_function, variables=None):
        """Adds a rate function to the model. Time dependent functions can receive
        the special ['time'] variable. Prints out a warning if an existing rate is
        overwritten.
        Examples:
            m.add_rate('v1',
                       lambda p, x: p.k1 * x,
                       ['x'])
            m.add_rate('v1',
                       lambda p, t, x: p.k1 * x * t,
                       ['time', 'x'])

        Parameters
        ----------
        rate_name : str
            Name of the rate function
        rate_function : callable
            Actual python method
        variables : list of str
            Model variables passed to the rate_function
        """
        if not isinstance(rate_name, str):
            raise TypeError("Rate name must be str")
        if not callable(rate_function):
            raise TypeError("Rate function must be a function")
        if variables is None:
            variables = []
        if not isinstance(variables, list):
            raise TypeError("Variables must be a list")

        for i in variables:
            if not isinstance(i, str):
                raise TypeError("Arguments must be str")

        if rate_name in self._rates:
            warnings.warn(f"Overwriting rate {rate_name}")

        self._rates[rate_name] = {"func": rate_function, "vars": variables}

    def _remove_rate(self, rate_name):
        """Removes a rate function from the model.

        Parameters
        ----------
        rate_name : str
            Name of the rate function

        Raises
        ------
        ValueError
            If rate name is not found in the model
        TypeError
            If rate name is not str
        """
        if isinstance(rate_name, str):
            if rate_name in self._rates:
                self._rates.pop(rate_name)
            else:
                raise ValueError("{} is not in the model".format(rate_name))
        else:
            raise TypeError("Function requires str input")

    def remove_rates(self, rate_names):
        """Removes a or multiple rate functions from the model.

        Parameters
        ----------
        rate_name : str or list of str
            Name of the rate function(s)

        Raises
        ------
        ValueError
            If rate name is not found in the model
        TypeError
            If rate name is not str or list of str
        """
        if isinstance(rate_names, str):
            self._remove_rate(rate_names)
        elif isinstance(rate_names, list):
            for rate_name in rate_names:
                self._remove_rate(rate_name)
        else:
            raise TypeError("Function requires str or list input")

    def get_rate_names(self):
        """Returns all rate names

        Returns
        -------
        rate_names : tuple[str]
            Names of all rates
        """
        return tuple(self._rates.keys())

    def get_rate_indexes(self, rate_name=None):
        v, k = zip(*enumerate(self.get_rate_names()))
        rate_idx = dict(zip(k, v))
        if rate_name is None:
            return rate_idx
        return rate_idx[rate_name]

    def get_rate_compounds(self, rate_name=None):
        """Returns the compounds (arguments) of a given rate function. If no rate name
        is supplied, the function returns a dictionary of the compounds of all rate functions.

        Parameters
        ----------
        rate_name : str
            Name of the rate

        Returns
        -------
        rate_compounds : list or dict
            The compound names of the rate
        """
        if rate_name is not None:
            return self._rates[rate_name]["vars"]
        else:
            return {
                module: module_dict["vars"]
                for module, module_dict in self._rates.items()
            }

    ##########################################################################
    # Algebraic Modules
    ##########################################################################

    def add_algebraic_module(
        self, module_name, algebraic_function, variables, derived_variables
    ):
        """ Adds an algebraic module. The algebraic_function must return an iterable. Prints
        a warning if algebraic module is already present in the model.

        Examples:
            m.add_algebraic_module('am1',
                                   lambda p, ATP: [p.A_total - ATP],
                                   ['ATP'],
                                   ['ADP'])

        Parameters
        ----------
        module_name : str
            Name of the module
        algebraic_function : callable
            Python method of the algebraic module
        variables : list
            Names of variables used for module
        derived_variables : list
            Names of compounds which are calculated by the module

        Raises
        ------
        TypeError
            If wrong types for any argument are used.
        """
        if not isinstance(module_name, str):
            raise TypeError("Module name must be str")
        if not callable(algebraic_function):
            raise TypeError("Algebraic function must be a function")
        if not isinstance(variables, list):
            raise TypeError("Variables must be a list")
        if not isinstance(derived_variables, list):
            raise TypeError("Derived variables must be a list")

        if module_name in self._algebraic_modules:
            warnings.warn(f"Overwriting algebraic module {module_name}")

        self._algebraic_modules[module_name] = {
            "func": algebraic_function,
            "vars": variables,
            "der_vars": derived_variables,
        }
        self._number_compounds()

    def add_algebraic_module_from_template(
        self, name, module_template, parameters, variables, derived_variables
    ):
        if parameters is None:
            parameters = []
        if variables is None:
            variables = []
        if derived_variables is None:
            derived_variables = []

        module_template = module_template(*parameters, variables, derived_variables)
        self._module_templates[name] = module_template

        self.add_algebraic_module(
            name, module_template.mod_func, variables, derived_variables
        )

    def _remove_algebraic_module(self, module_name):
        """Removes an algebraic module

        Parameters
        ----------
        module_name : str
            Name of the algebraic module

        Raises
        ------
        ValueError
            If name is not in the model
        """
        if not isinstance(module_name, str):
            raise TypeError("Function requires str input")

        if module_name in self._algebraic_modules:
            self._algebraic_modules.pop(module_name)
        else:
            raise ValueError("Module {} not in model".format(module_name))

    def update_algebraic_module(
        self, module_name, algebraic_function, variables, derived_variables
    ):
        if module_name in self._rates:
            func, m_vars, der_vars = self._algebraic_modules[module_name]
        if algebraic_function:
            func = algebraic_function
        if variables:
            m_vars = variables
        if derived_variables:
            der_vars = derived_variables

        self.remove_algebraic_modules(module_name)
        self.add_reaction(module_name, func, m_vars, der_vars)

    def remove_algebraic_modules(self, module_names):
        """Removes one or multiple algebraic modules

        Parameters
        ----------
        module_name : str or list of str
            Name of the algebraic module

        Raises
        ------
        ValueError
            If name is not in the model
        """
        if isinstance(module_names, str):
            self._remove_algebraic_module(module_names)
        elif isinstance(module_names, list):
            for module_name in module_names:
                self._remove_algebraic_module(module_name)
        else:
            raise TypeError("Function requires string or list input")
        self._number_compounds()

    def get_algebraic_module_compounds(self, module_name=None):
        """Returns the compounds (function arguments) of the algebraic module.
        If no module name is supplied, the compounds for all modules will be returned.

        Parameters
        ----------
        module_name : str
            Name of the algebraic module

        Returns
        -------
        module_compounds : list of str
            Compounds of the algebraic module
        Raises
        ------
        ValueError
            If module name is not in the model
        """
        if module_name is not None:
            if not isinstance(module_name, str):
                raise TypeError("Module name {} must be str".format(module_name))
            if module_name in self._algebraic_modules:
                return self._algebraic_modules[module_name]["vars"]
            else:
                raise ValueError("Module name {} not in model".format(module_name))
        else:
            return {
                module: module_dict["vars"]
                for module, module_dict in self._algebraic_modules.items()
            }

    def get_algebraic_module_derived_compounds(self, module_name=None):
        """Returns the derived compounds of the algebraic module.
        If no module name is supplied, the derived compounds for all modules will be returned.

        Parameters
        ----------
        module_name : str
            Name of the algebraic module

        Returns
        -------
        module_compounds : list of str
            Derived compounds of the algebraic module
        Raises
        ------
        ValueError
            If module name is not in the model
        """
        if module_name is not None:
            if not isinstance(module_name, str):
                raise TypeError("Module name {} must be str".format(module_name))
            if module_name in self._algebraic_modules:
                return self._algebraic_modules[module_name]["der_vars"]
            else:
                raise ValueError("Module name {} not in model".format(module_name))
        else:
            return {
                module: module_dict["der_vars"]
                for module, module_dict in self._algebraic_modules.items()
            }

    ##########################################################################
    # Reactions
    ##########################################################################

    def add_reaction(self, rate_name, rate_function, stoichiometries, variables=None):
        """Add a reaction to the model. Shortcut for add_rate and add stoichiometry functions.
        Additional variable ["time"] can be passed for time-dependent functions.

        Examples
        --------
            m.add_reaction('v1',
                           lambda p, x: p.k1 * x,
                           {'x': -1, 'y': 1},
                           ['x'])
            m.add_reaction('v1',
                           lambda p, t, x: p.k1 * x * t,
                           {'x': -1, 'y': 1},
                           ['time', 'x'])

        Parameters
        ----------
        rate_name : str
            Name of the rate
        rate_function : callable
            Python method of the rate
        stoichiometries : dict
            Dictionary containing the {compound:stoichiometry} pairs
        variables : list of str
            List containing the names of the compounds to be passed to the rate_function

        Raises
        ------
        TypeError
            If input types are violated
        """
        if variables is None:
            variables = []
        self.add_rate(rate_name, rate_function, variables)
        self.add_stoichiometry(rate_name, stoichiometries)

    def add_reaction_from_ratelaw(
        self,
        name,
        ratelaw,
        stoichiometries,
        parameters=None,
        substrates=None,
        modifiers=None,
    ):
        warnings.warn("Experimental method, API might change.", FutureWarning)
        if parameters is None:
            parameters = []
        if substrates is None:
            substrates = []
        if modifiers is None:
            modifiers = []

        ratelaw = ratelaw(*parameters, substrates, modifiers)
        self._ratelaws[name] = ratelaw

        self.add_reaction(
            name, ratelaw.rate_func, stoichiometries, substrates + modifiers
        )

    def remove_reactions(self, rate_names):
        """Removes a or multiple reactions from the model.

        Parameters
        ----------
        rate_names : str or list of str

        Raises
        ------
        TypeError
            If rate names is not str or list of str
        ValueError
            If reaction name not in the model
        """
        if isinstance(rate_names, str):
            self.remove_rates(rate_names)
            self.remove_stoichiometries(rate_names)
        elif isinstance(rate_names, list):
            for rate_name in rate_names:
                self.remove_rates(rate_name)
                self.remove_stoichiometries(rate_name)
        else:
            raise TypeError("Function requires string or list input")

    def update_reaction(
        self, rate_name=None, rate_function=None, stoichiometries=None, variables=None
    ):
        if rate_name in self._rates:
            func, r_vars = self._rates[rate_name]
            stoich = self._stoichiometries[rate_name]
        if rate_function is not None:
            func = rate_function
        if stoichiometries is not None:
            stoich = stoichiometries
        if variables is not None:
            r_vars = variables

        self.remove_reactions(rate_name)
        self.add_reaction(rate_name, func, stoich, r_vars)

    ##########################################################################
    # Simulation functions
    ##########################################################################

    def get_full_concentration_dict(self, y0):
        """Calculates the full concentration vector including the derived variables.
        Takes either a dictionary or list/array input and returns a dictionary.

        Parameters
        ----------
        y0 : Dict
            concentration dictionary

        Returns
        -------
        y_full : dict
            Dictionary containing all compounds and derived compounds
        """
        if isinstance(y0, dict):
            y0 = y0.copy()
            for amod in self._algebraic_modules.values():
                try:
                    for i, j in zip(
                        amod["der_vars"],
                        amod["func"](
                            self._parameters, *[y0[var] for var in amod["vars"]]
                        ),
                    ):
                        y0[i] = j
                except TypeError:
                    raise TypeError(f"Algebraic module {amod} does not return iterable")
            return y0
        elif isinstance(y0, (list, np.ndarray)):
            y0 = dict(zip(self._compounds, y0))
            return self.get_full_concentration_dict(y0)
        else:
            raise TypeError("Requires dict or list/array input")

    def _get_fluxes(self, t, y_full):
        """Calculates the fluxes at time point(s) t
        This is the performance optimized version of the function

        Parameters
        ----------
        t : int, float, list / array of int / float
            Time point(s)
        y_full : dictionary
            Full concentration dictionary (obatained by get_full_concentration_dict)

        Returns
        -------
        rates : dict
            Dictionary containing all calculated rates
        """
        y_full["time"] = t
        fluxes = {}
        for name, rate in self._rates.items():
            fluxes[name] = rate["func"](
                self._parameters, *[y_full[var] for var in rate["vars"]]
            )
        return fluxes

    def get_rates(self, t, y_full):
        """Alias for get_fluxes"""
        warnings.warn(
            "Function to be replaced by get_fluxes in modelbase 0.4.0",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.get_fluxes(t, y_full)

    def get_fluxes(self, t, y_full):
        """Calculates the rates at time point(s) t

        Parameters
        ----------
        t : int, float, list / array of int / float
            Time point(s)
        y_full : dictionary
            Full concentration dictionary (obatained by get_full_concentration_dict)

        Returns
        -------
        rates : dict
            Dictionary containing all calculated rates
        """
        if isinstance(y_full, dict):
            y_full = (
                y_full.copy()
            )  # This is necessary, such that get_rates does not alter it
        else:
            y_full = self.get_full_concentration_dict(y_full)
        if isinstance(t, int):
            len_t = 1
        else:
            len_t = len(t)
        y_full["time"] = t
        rates = {}
        try:
            for name, rate in self._rates.items():
                rate = rate["func"](
                    self._parameters, *[y_full[var] for var in rate["vars"]]
                )
                try:
                    len(rate)
                    rates[name] = rate
                except TypeError:  # Singleton instead of array
                    rates[name] = np.ones(len_t) * rate
        except KeyError as e:
            raise KeyError(f"Could not find {e} for rate {name}")
        return rates

    def get_rates_array(self, t, y_full):
        """Alias for get_flux_array"""
        warnings.warn(
            "Function to be replaced by get_flux_array in modelbase 0.4.0",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.get_flux_array(t, y_full)

    def get_flux_array(self, t, y_full):
        """Alias for get_rates_array"""
        rates = self.get_fluxes(t, y_full)
        return np.array([i for i in rates.values()])

    def _get_rhs(self, t, y0):
        """Calculates the right hand side of the ODE system. This is the more performant
        version of get_right_hand_side() and thus returns only an array instead of a dictionary.

        Parameters
        ----------
        t : int, float, list / array of int / float
            Time point(s)
        y0 : (list or array) or dict
            Concentration vector

        Returns
        -------
        rhs : list
            List of the right hand side
        """
        if not self._stoichiometries_by_compounds:
            self._stoichiometries_by_compounds = self.get_stoichiometries("Compounds")

        y0 = dict(zip(self._compounds, y0))
        rates = self._get_fluxes(t, self.get_full_concentration_dict(y0))
        compounds_local = self._compounds
        dxdt = dict(zip(compounds_local, np.zeros(len(compounds_local))))
        for k, stoc in self._stoichiometries_by_compounds.items():
            for rate, n in stoc.items():
                dxdt[k] += n * rates[rate]
        return [dxdt[i] for i in compounds_local]

    def get_right_hand_side(self, t, y0):
        """Calculate the right hand side of the ODE system

        Parameters
        ----------
        t : float
            Time point
        y0 : dict
            Initial concentrations
        """
        if isinstance(y0, dict):
            y0 = [y0[i] for i in self._compounds]
        rhs = self._get_rhs(t, y0)
        eqs = [f"d{cpd}dt" for cpd in self.get_stoichiometries("Compounds")]
        return dict(zip(eqs, rhs))

    def get_stoichiometry_matrix(self):
        """Return the stoichiometric matrix

        Returns
        -------
        stoichiometric_matrix : np.array
        """
        M = np.array(np.zeros([len(self._compounds), len(self._rates)]))
        for i, r in enumerate(self._rates):
            for k, v in self._stoichiometries[r].items():
                M[self._compounds[k], i] = v

        return M

    def get_stoichiometry_df(self):
        """Return the stoichiometric matrix as a pandas DataFrame

        Returns
        -------
        stoichiometric_matrix : pd.DataFrame
        """

        return pd.DataFrame(
            self.get_stoichiometry_matrix(), self.get_compounds(), self.get_rate_names()
        )

    def check_for_compounds_without_reactions(self):
        df = self.get_stoichiometry_df()
        return df[~df.any(axis=1)].index.values.tolist()
