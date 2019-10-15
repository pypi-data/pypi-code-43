import copy
import pprint


class ParameterSet:
    """Class containing model paramters

    Attributes
    ----------
    parameters : dict or ParameterSet
        Supplied parameters
    """

    def __init__(self, parameters=None):
        if parameters is None:
            parameters = {}
        if isinstance(parameters, dict):
            for k, v in parameters.items():
                setattr(self, k, v)
        elif isinstance(parameters, ParameterSet):
            for k, v in parameters.__dict__.items():
                setattr(self, k, v)
        else:
            raise TypeError("Init requires dict or ParameterSet input")

    def __str__(self):
        return pprint.pformat(self.__dict__)

    def __repr__(self):
        return pprint.pformat(self.__dict__)

    def copy(self):
        return copy.deepcopy(self)

    def add_parameter(self, key, value):
        """Adds new parameters.
        Does not overwrite existing parameters.
        Use the update_parameter or add_and_update parameter methods in this case.

        Attributes
        ----------
        key : str
            parameter name
        value : int or float
            parameter value

        Raises
        ------
        ValueError
            If key is already in the model
        """
        if key in self.__dict__.keys():
            raise ValueError(
                "Key {} is already in the model. Please use the update_parameters method".format(
                    key
                )
            )
        else:
            setattr(self, key, value)

    def update_parameter(self, key, value):
        """Updates parameters.
        Does not add new parameters.
        Use the add_parameter or add_and_update parameter methods in this case.

        Attributes
        ----------
        key : str
            parameter name
        value : int or float
            parameter value

        Raises
        ------
        ValueError
            If key is not in the model
        """
        if key in self.__dict__.keys():
            setattr(self, key, value)
        else:
            raise ValueError(
                "Key {} is not in the model. Please use the add_parameters method".format(
                    key
                )
            )

    def add_and_update_parameter(self, key, value):
        """Adds new and updates existing parameters.

        Attributes
        ----------
        key : str
            parameter name
        value : int or float
            parameter value
        """
        setattr(self, key, value)

    def remove_parameter(self, name):
        """Removes parameter from ParameterSet

        Attributes
        ----------
        name : str
            Name of the parameter to be removed
        """
        if name in self.__dict__:
            delattr(self, name)
        else:
            raise ValueError("Key {} is not in the model".format(name))
