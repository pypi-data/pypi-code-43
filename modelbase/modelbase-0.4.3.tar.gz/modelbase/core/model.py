import collections
import pickle
import json
import warnings
import copy

from .parameterset import ParameterSet


class Model:
    """A class containing basic compound and stoichiometric functions, that are shared among
    all model classes.
    """

    def __init__(self):
        self._compounds = {}
        self._stoichiometries = {}

    def __enter__(self):
        self._copy = self.copy()
        return self.copy()

    def __exit__(self, exception_type, exception_value, exception_traceback):
        # Restore any changes made to the model
        self.__dict__ = self._copy.__dict__

    def copy(self):
        """Returns a deepcopy of the model

        Returns
        -------
        model
            Deepcopy of the model object
        """
        return copy.deepcopy(self)

    ##########################################################################
    # Compound functions
    ##########################################################################

    def _number_compounds(self):
        # type () -> None
        """Numerates the compounds."""
        for number, compound in enumerate(self._compounds):
            self._compounds[compound] = number

    def _add_compound(self, compound):
        """Adds a single compound to the model.

        Parameters
        ----------
        compound : str
            Name of the compound

        Raises
        ------
        ValueError
            If compound is already in the model
        TypeError
            If compound name is not str
        """
        if isinstance(compound, str):
            if compound != "time":
                if compound not in self._compounds:
                    self._compounds[compound] = None
                else:
                    raise ValueError("{} is already in compounds".format(compound))
            else:
                raise ValueError("time is a protected variable for time")
        else:
            raise TypeError("Function requires string input")

    def add_compounds(self, compounds):
        """Adds compounds to the model.

        Parameters
        ----------
        compound : str or list[str]
            Name of the compound(s)

        Raises
        ------
        ValueError
            If compound is already in the model
        TypeError
            If compound name is not str
        """
        if isinstance(compounds, list):
            for compound in compounds:
                self._add_compound(compound)
        elif isinstance(compounds, str):
            self._add_compound(compounds)
        else:
            raise TypeError("Function requires list input")
        self._number_compounds()

    def _remove_compound(self, compound):
        """Removes a single compound from the model

        Parameters
        ----------
        compound : str
            Name of the compound

        Raises
        ------
        ValueError
            If compound is already in the model
        TypeError
            If compound name is not str
        """
        if isinstance(compound, str):
            if compound in self._compounds:
                self._compounds.pop(compound)
            else:
                raise ValueError("{} not in compounds".format(compound))
            if compound in self.get_stoichiometries("Compounds"):
                reactions = list(self.get_stoichiometries("Compounds")[compound].keys())
                warnings.warn(f"Compound still in reactions {reactions}")
        else:
            raise TypeError("Function requires list or string input")

    def remove_compounds(self, compounds):
        """Removes a single or multiple compounds from the model

        Parameters
        ----------
        compound : str or list[str]
            Name of the compound(s)

        Raises
        ------
        ValueError
            If compound is already in the model
        TypeError
            If compound name is not str
        """
        if isinstance(compounds, list):
            for compound in compounds:
                self._remove_compound(compound)
        elif isinstance(compounds, str):
            self._remove_compound(compounds)
        else:
            raise TypeError("Function requires list or string input")
        self._number_compounds()

    def get_compounds(self):
        """Returns the model compounds and their ids.

        Returns
        -------
        compounds : dict
        """
        return self._compounds

    def get_compound_names(self):
        """Returns the names of the model compounds.

        Returns
        -------
        compound_names : list[str]
        """
        return list(self._compounds.keys())

    ##########################################################################
    # Stoichiometries
    ##########################################################################

    def add_stoichiometry(self, rate_name, stoichiometries):
        """Adds the stoichiometry of one rate to the model

        Example: "v1", {"x": 1}

        Parameters
        ----------
        rate_name : str
            Name of the rate
        stoichiometries : dict
            Dictionary containing the compound:stoichiometry pair(s)

        Raises
        ------
        TypeError
            If input types are wrong

        """
        if not isinstance(rate_name, str):
            raise TypeError("Rate name {} must be str".format(rate_name))
        if not isinstance(stoichiometries, dict):
            raise TypeError("Stoichiometries must be dict.")

        self._stoichiometries[rate_name] = stoichiometries

    def add_stoichiometries(self, stoichiometries):
        """Adds the stoichiometry of one or multiple rates to the model

        Example: {"v1": {"x": -1, "y": 1},
                  "v2": {"x": 1, "y": -1}}

        Parameters
        ----------
        stoichiometries : nested dict
            Dictionary containing the {rate:{compound:stoichiometry}} pair(s)

        Raises
        ------
        TypeError
            If input types are wrong

        """
        if isinstance(stoichiometries, dict):
            for key, value in stoichiometries.items():
                self.add_stoichiometry(key, value)
        else:
            raise TypeError("Function expects dict input")

    def add_stoichiometry_by_compound(self, compound_name, stoichiometry):
        """Adds the stoichiometry of a single compound to the model

        Example: "x", {"v1": 1}

        Parameters
        ----------
        compound_name : str
            Name of the compound
        stoichiometry : dict
            Dictionary containing the {rate_name:stoichiometry}

        Raises
        ------
        TypeError
            If input types are wrong

        """
        if not isinstance(compound_name, str):
            raise TypeError("Compound name {} must be str".format(compound_name))
        if not isinstance(stoichiometry, dict):
            raise TypeError("Stoichiometries must be dict.")

        for key, value in stoichiometry.items():
            if key not in self._stoichiometries:
                self._stoichiometries[key] = {}
            self._stoichiometries[key][compound_name] = value

    def add_stoichiometries_by_compounds(self, stoichiometries):
        """Adds the stoichiometry of one or multiple compounds to the model

        Example: {"x": {"v1": -1, "v2": 1},
                  "y": {"v1": 1, "v2": -1}}

        Parameters
        ----------
        stoichiometries : nested dict
            Dictionary containing the {compound:{rate:stoichiometry}} pair(s)

        Raises
        ------
        TypeError
            If input types are wrong

        """
        if isinstance(stoichiometries, dict):
            for k, v in stoichiometries.items():
                self.add_stoichiometry_by_compound(k, v)
        else:
            raise TypeError("Function expects dict input")

    def _remove_stoichiometry(self, rate_name):
        """Removes a single rate stoichiometry from the model

        Parameters
        ----------
        rate_name : str
            name of the rate

        Raises
        ------
        ValueError
            If rate name is not in the model
        TypeError
            If rate name is not str
        """
        if not isinstance(rate_name, str):
            raise TypeError("Rate_name {} must be str".format(rate_name))
        if rate_name in self._stoichiometries:
            self._stoichiometries.pop(rate_name)
        else:
            raise ValueError("Stoichiometry {} not in model".format(rate_name))

    def remove_stoichiometries(self, rate_names):
        """Removes a single or multiple rate stoichiometries from the model

        Parameters
        ----------
        rate_names : str or list of str
            name of the rates

        Raises
        ------
        ValueError
            If rate name is not in the model
        TypeError
            If rate name is not str or list of str
        """
        if isinstance(rate_names, list):
            for rate_name in rate_names:
                self._remove_stoichiometry(rate_name)
        elif isinstance(rate_names, str):
            self._remove_stoichiometry(rate_names)
        else:
            raise TypeError("Function requires list or string input")

    def get_stoichiometries(self, by="Reactions"):
        """Returns stoichiometries, either ordered by Reactions or Compounds

        Parameters
        ----------
        by : {'Reactions', 'Compounds'}
            Return ordering of the function. Either Reactions or Compounds

        Returns
        -------
        stoichiometries : dict
            Stoichiometries sorted either by reactions or by compounds
        """
        if by == "Reactions":
            return self._stoichiometries
        elif by == "Compounds":
            flipped = collections.defaultdict(dict)
            for key, val in self._stoichiometries.items():
                for subkey, subval in val.items():
                    flipped[subkey][key] = subval
            return dict(flipped)
        else:
            raise ValueError("Can only be sorted by 'Reactions' or 'Compounds'.")


class ParameterModel(Model):
    """Base class adding parameter functions"""

    def __init__(self, parameters=None):
        super().__init__()
        if parameters is None:
            parameters = {}
        self._parameters = ParameterSet(parameters)
        self._original_parameters = self._parameters.copy()

    ##########################################################################
    # Parameter functions
    ##########################################################################
    def add_parameters(self, new_parameters):
        """Adds new parameters to the model.
        Does not overwrite existing parameters.
        Use the update_parameters or add_and_update parameters methods in this case.

        Attributes
        ----------
        new_parameters : dict or modelbase.core.ParameterSet
            Dictionary containing the parameter and value pairs

        Raises
        ------
        ValueError
            If key is already in the model
        TypeError
            If new_parameters is neither dict nor ParameterSet
        """
        if isinstance(new_parameters, dict):
            for k, v in new_parameters.items():
                self._parameters.add_parameter(k, v)
        elif isinstance(new_parameters, ParameterSet):
            self.add_parameters(new_parameters.__dict__)
        else:
            raise TypeError("Function requires dict or ParameterSet input")

    def update_parameters(self, parameter_update):
        """Updates model parameters.
        Does not add new parameters.
        Use the add_parameters or add_and_update parameters methods in this case.

        Attributes
        ----------
        parameter_update : dict or modelbase.ParameterSet
            Dictionary containing the parameter and value pairs

        Raises
        ------
        ValueError
            If key is not in the model
        TypeError
            If new_parameters is neither dict nor ParameterSet
        """
        if isinstance(parameter_update, dict):
            for k, v in parameter_update.items():
                self._parameters.update_parameter(k, v)
        elif isinstance(parameter_update, ParameterSet):
            self.update_parameters(parameter_update.__dict__)
        else:
            raise TypeError("Function requires dict or ParameterSet input")

    def add_and_update_parameters(self, parameters):
        """Adds new and updates existing model parameters.

        Attributes
        ----------
        parameters : dict or modelbase.ParameterSet
            Dictionary containing the parameter and value pairs

        Raises
        ------
        TypeError
            If new_parameters is neither dict nor ParameterSet
        """
        if isinstance(parameters, dict):
            for k, v in parameters.items():
                self._parameters.add_and_update_parameter(k, v)
        elif isinstance(parameters, ParameterSet):
            self.add_and_update_parameters(parameters.__dict__)
        else:
            raise TypeError("Function requires dict or ParameterSet input")

    def remove_parameters(self, parameters):
        """ Removes parameters from the model

        Attributes
        ----------
        parameters : list or str
            Names of the parameters that should be removed
        """
        if isinstance(parameters, list):
            for key in parameters:
                self._parameters.remove_parameter(key)
        elif isinstance(parameters, str):
            self._parameters.remove_parameter(parameters)
        else:
            raise TypeError("Function requires list or string input")

    def store_parameters_to_file(self, filename, filetype="json"):
        """Stores the ParameterSet object into a json or pickle file

        Parameters
        ----------
        filename : str
            The name of the pickle file
        filetype : str
            Output file type. Json or pickle.
        """
        if filetype == "json":
            with open(filename, "w") as f:
                json.dump(self._parameters.__dict__, f)
        elif filetype == "pickle":
            with open(filename, "wb") as f:
                pickle.dump(self._parameters.__dict__, f)
        else:
            raise ValueError("Can only save to json or pickle")

    def load_parameters_from_file(self, filename, filetype="json"):
        """Loads the ParameterSet object from a json or pickle file

        Parameters
        ----------
        filename : str
            The name of the pickle file
        filetype : str
            Output file type. Json or pickle.
        """
        if filetype == "json":
            self.add_parameters(json.load(open(filename, "r")))
        elif filetype == "pickle":
            self.add_parameters(pickle.load(open(filename, "rb")))
        else:
            raise ValueError("Can only save to json or pickle")

    def restore_parameters(self):
        """Set parameters to initialization parameters"""
        self._parameters = self._original_parameters.copy()

    def get_parameter(self, parameter_name):
        """Returns a single parameter

        Parameters
        ----------
        parameter_name : str
            Name of the parameter

        Returns
        -------
        parameter : (int, float)
            Value of the parameter
        """
        return self._parameters.__dict__[parameter_name]

    def get_all_parameters(self, return_type="dict"):
        """Returns the parameters as a dictionary or ParameterSet object.

        Parameters
        ----------
        return_type : str
            The return type of the function. Either dict or ParameterSet

        Returns
        -------
        parameters : dict or modelbase.ParameterSet
        """

        if return_type == "dict":
            return self._parameters.__dict__
        elif return_type == "ParameterSet":
            return self._parameters
        else:
            raise ValueError("Can only return dict or ParameterSet")
