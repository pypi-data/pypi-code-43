from controlpyweb.io_definitions.single_io import SingleIO
from controlpyweb.io_definitions.io_out import IOOut
from controlpyweb.abstract_reader_writer import AbstractReaderWriter
from str2bool import str2bool


class DiscreteIn(SingleIO):
    def __init__(self, name: str, addr: str, default: bool = False,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)

    @staticmethod
    def _convert_type(value):
        if isinstance(value, str):
            return str2bool(value)
        return bool(value)

    def __bool__(self):
        return bool(self.value)


class DiscreteOut(IOOut, DiscreteIn):
    def __init__(self, name: str, addr: str, default: bool = False,
                 reader: AbstractReaderWriter = None, *args, **kwargs):
        super().__init__(name, addr, default, reader, *args, **kwargs)





