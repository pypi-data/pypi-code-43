# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:27:05 2018

@author: Rastko
"""
from abc import ABC, abstractmethod, abstractproperty
import visa
import validate

class Instrument(ABC):
    """Class for all instrument drivers that requires suclasses to implement three basic methods:
    init
    close
    reset

    """
    def __init__(self, online=True, address=None, name=None):
        """One-line docString"""
        self.online = online
        self._address = address
        self._name = name
        self._rm = visa.ResourceManager()
        self.instr = self._rm.open_resource(address)
        
    def _is_offline(self):
        """A method for checking if the instrument is online"""
        if not self.online:
            print('Warning: {:16s} is offline.'.format(self._name))
            return True
        else:
            return False
    
    def write(self, command):
        """Write a command to the instruments"""
        self.instr.write(command)


    def read(self, command):
        """Read a command to the instruments"""
        self.instr.read(command)


    def query(self, command):
        """Query a command to the instruments"""
        self.instr.query(command)

    @abstractmethod
    def __enter__(self):
        pass
    
    @abstractmethod
    def reset(self):
        """One-line docString"""
        pass

    @abstractmethod
    def __exit__(self):
        pass

    @staticmethod
    def prop(set_command, docs,
             in_range=None,
             in_set=None,
             ):
        """Property generator with in_range/set validation
        
        Parameters
        ----------
        set_command : STR
            Command to communicate with the instrument, example: ':OUTP {:s}'
        docs : STR
            Documentation string for property setter
        in_range : list, tuple
            (min, max) range validator for the property values
        in_set : list, dict
            [allowed_values] discrete validator for the property values
        
        Returns
        -------
        Property
            Property of the Instrument class
        """
        # check that function arguments have been supplied properly
        conditions = 0
        if in_range is not None:
            conditions += 1
            condition = in_range
            check_validity = validate.in_range  # set validator function
            allowed_values = in_range
        if in_set is not None:
            conditions += 1
            condition = in_set
            check_validity = validate.in_set  # set validator function
            try:
                allowed_values = in_set.keys()
            except AttributeError:
                allowed_values = in_set
        if conditions != 1:
            raise ValueError('You can set either in_range or in_set, '
                             'not both or neither')

        def fget(self):
            if in_range is not None:
                print('Allowed range is from {} to {}'.format(min(in_range),
                                                              max(in_range)))
            if in_set is not None:
                print('Allowed values are {}'.format(allowed_values))
            return allowed_values

        def fset(self, value):
            value = check_validity(value, condition)
            self.write(set_command % value)

        # Add the specified document string to the getter
        fget.__doc__ = docs

        return property(fget, fset)
