from controlpyweb.io_definitions.single_io import SingleIO
from controlpyweb.abstract_reader_writer import AbstractReaderWriter


class IOOut(SingleIO):
    def __init__(self, name: str, addr: str, default, reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)
        self.ignore_duplicate_writes = kwargs.get('ignore_duplicate_writes', True) if kwargs is not None else True

    def __set__(self, instance, value):
        if hasattr(value, 'value'):
            value = value.value
        self.write(value)

    def write(self, value):
        if self.ignore_duplicate_writes and value == self.value:
            return
        self._reader_writer.write(self.addr, self._convert_type(value))

    def write_immediate(self, value):
        self._reader_writer.write_immediate(self.addr, self._convert_type(value))