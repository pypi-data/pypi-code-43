"""Fields for edition 1 GRIB messages."""

from pupygrib import base
from pupygrib import binary


class FloatField(base.Field):
    """A 32-bit GRIB 1 floating point field."""

    def get_value(self, section, offset):
        return binary.unpack_grib1float_from(section._data, offset)
