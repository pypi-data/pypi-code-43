# (c) 2015-2017 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import os
from .protocolinterface import ensurelist
import abc


class _Validator:
    @abc.abstractmethod
    def validate(self, value):
        pass

    def __str__(self):
        return str(self.__class__.__name__).lower()

    def __repr__(self):
        return self.__str__()


class Boolean(_Validator):
    def validate(self, value):
        if not isinstance(value, bool):
            raise TypeError('the value "{}" must be boolean'.format(value))


class Object(_Validator):
    def __init__(self, classname):
        self.classname = classname

    def validate(self, value):
        classname = self.classname
        classname = ensurelist(classname)

        valid = False
        for cl in classname:
            if isinstance(value, cl):
                valid = True
                break
        if not valid:
            raise TypeError('the value "{}" must be an object of {}'.format(value, self.classname))


class Class(_Validator):
    def __init__(self, classname):
        self.classname = classname

    def validate(self, value):
        classname = self.classname
        classname = ensurelist(classname)

        valid = False
        for cl in classname:
            if issubclass(value, cl):
                valid = True
                break
        if not valid:
            raise TypeError('the value "{}" must be subclass of {}'.format(value, self.classname))


class Function(_Validator):
    def validate(self, value):
        # Supporting delayed functions which are passed as function/arguments tuples
        if not (hasattr(value, '__call__') or (isinstance(value, tuple) and hasattr(value[0], '__call__'))):
            raise TypeError('the value "{}" must be a function or (function, (args,)) tuple.'.format(value))

    @staticmethod
    def fixDelayedTuples(value):
        if isinstance(value, tuple) and len(value) in [2, 3] and \
                hasattr(value[0], '__call__') and not hasattr(value[1], '__call__'):
            return [value]
        return value


class String(_Validator):
    def validate(self, value):
        if not isinstance(value, str):
            raise ValueError('the value "{}" must be a string'.format(value))


class Dictionary(_Validator):
    def __init__(self, key_type=None, valid_keys=None, value_type=None, valid_values=None):
        self.key_type = key_type
        self.valid_keys = valid_keys
        self.value_type = value_type
        self.valid_values = valid_values

    def validate(self, value):
        if not isinstance(value, dict):
            raise TypeError('the value "{}" must be a dictionary.'.format(value))
        for k in value.keys():
            if self.key_type is not None and not isinstance(k, self.key_type):
                raise TypeError('the key "{}" is not of type {}'.format(k, self.key_type))
            if self.valid_keys is not None and k not in self.valid_keys:
                raise TypeError('the key "{}" is not valid (valid keys: {})'.format(k, ', '.join(self.valid_keys)))
            if self.value_type is not None:
                if k in self.value_type.keys():
                    if not isinstance(value[k], self.value_type[k]):
                        raise TypeError('the value "{}" of key "{}" is not of type '
                                        '{}'.format(value[k], k, self.value_type[k]))
            if self.valid_values is not None:
                if k in self.valid_values.keys():
                    if value[k] not in self.valid_values[k]:
                        raise TypeError('the value "{}" of key "{}" is not valid (valid values for this '
                                        'key: {})'.format(value[k], k, ', '.join(self.valid_values[k])))


class File(_Validator):
    def __init__(self, exist=False, writable=False, basedir=None):
        self.must_exist = exist
        self.writable = writable
        self.basedir = basedir

    def validate(self, value):
        if self.must_exist:
            found = False
            if self.basedir and os.path.isfile(os.path.join(self.basedir, value)):
                value = os.path.join(self.basedir, value)
                found = True
            if not found and os.path.isfile(value):
                found = True
            if not found:
                raise FileExistsError('the file "{}" does not exist'.format(value))
            if not os.access(value, os.R_OK):
                raise PermissionError('the file "{}" cannot be read'.format(value))
        if self.writable:
            if self.basedir:
                value = os.path.join(self.basedir, value)
            try:
                f = open(value, "a+")
                f.close()
            except:
                raise PermissionError('the file "{}" is not writeable'.format(value))


# TODO: Create directory validator

class Number(_Validator):
    def __init__(self, datatype, valid_range):
        """ Validates numbers

        Parameters
        ----------
        datatype : type
            A datatype like int or float
        valid_range : str
            A string describing the valid range of values. Choose between: 'POS', '0POS', 'NEG', '0NEG', 'ANY'
        """

        self.valid_range = valid_range
        self.datatype = datatype

    def validate(self, value):
        valid_range = self.valid_range
        try:
            if self.datatype is float and isinstance(value, int):
                return
            if not isinstance(value, self.datatype):
                raise TypeError('the value "{}" is not {}'.format(value, self.datatype))

            if valid_range == 'POS' and value <= 0:
                raise ValueError('the value "{}" must be > 0'.format(value))
            if valid_range == '0POS' and value < 0:
                raise ValueError('the value "{}" must be >=0'.format(value))
            if valid_range == 'NEG' and value >= 0:
                raise ValueError('the value "{}" must be < 0'.format(value))
            if valid_range == '0NEG' and value > 0:
                raise ValueError('the value "{}" must be <=0'.format(value))
        except NameError as e:
            raise NameError(e)

