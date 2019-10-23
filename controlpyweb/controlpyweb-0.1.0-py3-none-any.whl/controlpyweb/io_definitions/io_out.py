"""
Module IO Out:
The IOOut class provides implementation specific to analog and discrete outputs.
"""

from controlpyweb.io_definitions.single_io import SingleIO
from controlpyweb.abstract_reader_writer import AbstractReaderWriter
from abc import ABC


class IOOut(SingleIO, ABC):

    def __init__(self, name: str, addr: str, default, reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)
        self.ignore_duplicate_writes = kwargs.get('ignore_duplicate_writes', True) if kwargs is not None else True

    def __set__(self, instance, value):
        if hasattr(value, 'value'):
            value = value.value
        self.write(value)

    def write(self, value):
        """ Stores the given value in a cache that will be written when the call to send hardware is made. """
        if self.ignore_duplicate_writes and value == self.value:
            return
        self._reader_writer.write(self.addr, self._convert_type(value))

    def write_immediate(self, value):
        """ Immediately sends the value to the hardware. This method should be used sparingly given the round
        trip time of appx 20ms."""
        self._reader_writer.write_immediate(self.addr, self._convert_type(value))