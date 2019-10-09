# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 19:27:05 2018

@author: Rastko
"""
from abc import ABC, abstractmethod  # , abstractproperty
import visa
import validate


class Instrument(ABC):
    """Class for all instruments that requires three basic methods:
    
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
        # self.instr = self._rm.open_resource(address)
        
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

    def read(self):
        """Read a command to the instruments"""
        return self.instr.read()

    def query(self, command):
        """Query a command to the instruments"""
        return self.instr.query(command)

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
             name='Value',
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
                print('{} takes values from {} to {}'.format(name,
                                                             min(in_range),
                                                             max(in_range)))
            if in_set is not None:
                print('{} can be {}'.format(name, allowed_values))
            return allowed_values

        def fset(self, value):
            value = check_validity(value, condition, name)
            self.write(set_command.format(value))
            # print(value)

        # Add the specified document string to the getter
        fget.__doc__ = docs

        return property(fget, fset)

# testing
if __name__ == "__main__":
    class Test(Instrument):
        konj = 2
        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def reset(self):
            print(self.konj)
            pass

        resolution = Instrument.prop('whatever {}', 'This is the docstring',
                                     in_set={
                                                '20 MHz': 1,
                                                '100 MHz': 2,
                                            },
                                     name='resolution',
                                     )
        output = Instrument.prop('whatever {}', 'a', in_set=['ON', 'OFF'],
                                 name='output')

    a = Test()
        
