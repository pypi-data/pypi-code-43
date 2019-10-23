"""
Module: Single IO
The SingleIO class provides a base for all IO type. It adds common functionality, where possible, to
be inherited by all.
"""

from controlpyweb.abstract_reader_writer import AbstractReaderWriter
import threading
from controlpyweb.errors import ControlPyWebReadOnlyError
from abc import ABC, abstractmethod


class SingleIO(ABC):

    def __init__(self, name: str, addr: str, default: object, namespace: str = None,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        self.units = kwargs.get("units") if kwargs is not None else ""
        self.name = name
        self.addr = addr
        self.namespace = namespace
        self._reader_writer = reader
        self._default = default

    def __and__(self, other):
        if hasattr(other, 'value'):
            return self.value and other.value
        return self.value and other

    def __eq__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value == other

    def __float__(self):
        return float(self.value)

    def __int__(self):
        return int(self.value)

    def __ne__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value != other

    def __gt__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value > other

    def __lt__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value < other

    def __ge__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value >= other

    def __le__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value <= other

    def __get__(self, instance, owner):
        self.read()
        return self

    def __set__(self, obj, value):
        raise ControlPyWebReadOnlyError

    def __str__(self):
        return '[{}] {} = {}'.format(type(self).__name__, self.name, self.value)

    def __add__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value + other

    def __sub__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value - other

    def __mul__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value * other

    def __truediv__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value / other

    def __floordiv__(self, other):
        if hasattr(other, 'value'):
            other = other.value
        return self.value // other

    @property
    def value(self):
        """
        Provides a property to pull the value of the object, this is the same as IO.read()
        :return: Returns the value, converted to the appropriate data type. If the value is none, returns
        the default value for the IO.
        """
        val = self.read()
        if val is None:
            return self._default
        return self._convert_type(val)

    @staticmethod
    @abstractmethod
    def _convert_type(value):
        """ For derived classes, this method should convert the incoming to the appropriate data type for the
        specif IO """
        pass

    def read(self):
        """
        Retrieves the last value of the IO after reading from hardware or after last write.
        :return: Returns the value, converted to the appropriate data type.
        """
        if self._reader_writer is None:
            return None
        val = self._reader_writer.read(self.addr)
        val = self._convert_type(val)
        return val

    def read_immediate(self):
        """
        Makes an immediate call to the hardware to read the value. This method should be used sparingly as it
        generally takes in order of 20ms to do a read.
        :return: Returns the latest value retrieved from hardware.
        """
        val = self._reader_writer.read_immediate(self.addr)
        val = self._convert_type(val)
        return val











