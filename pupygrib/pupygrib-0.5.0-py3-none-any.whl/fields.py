"""Field descriptors for GRIB message sections."""

from pupygrib import binary


class Field:
    """Base class for field descriptors of GRIB message sections.

    A field descriptor is responsible for converting binary octets of
    a GRIB message to Python objects.  The *octet* argument should be
    the 1-based index of the first octet that the field represents.

    """

    def __init__(self, octet):
        self.offset = octet - 1  # octet is 1-based

    def __get__(self, section, sectiontype):
        if section is None:
            return self
        value = self.get_value(section, self.offset)
        # By putting the value in the section instance's __dict__,
        # this descriptor shouldn't be used the next time the
        # attribute is looked up.
        section.__dict__[self.name] = value
        return value


class BytesField(Field):
    """A raw bytes field.

    If a *size* is not given, all bytes until the end of the section
    will be included.

    """

    def __init__(self, octet, size=None):
        super().__init__(octet)
        self.size = size

    def get_value(self, section, offset):
        return section._data[offset : self.size and offset + self.size].tobytes()


class Int8Field(Field):
    """An 8-bit signed magnitude integer field."""

    def get_value(self, section, offset):
        return binary.unpack_int8_from(section._data, offset)


class Int16Field(Field):
    """A 16-bit signed magnitude integer field."""

    def get_value(self, section, offset):
        return binary.unpack_int16_from(section._data, offset)


class Int24Field(Field):
    """A 24-bit signed magnitude integer field."""

    def get_value(self, section, offset):
        return binary.unpack_int24_from(section._data, offset)


class Uint8Field(Field):
    """An 8-bit unsigned integer field."""

    def get_value(self, section, offset):
        return binary.unpack_uint8_from(section._data, offset)


class Uint16Field(Field):
    """A 16-bit unsigned integer field."""

    def get_value(self, section, offset):
        return binary.unpack_uint16_from(section._data, offset)


class Uint24Field(Field):
    """A 24-bit unsigned integer field."""

    def get_value(self, section, offset):
        return binary.unpack_uint24_from(section._data, offset)


class Uint32Field(Field):
    """A 32-bit unsigned integer field."""

    def get_value(self, section, offset):
        return binary.unpack_uint32_from(section._data, offset)


class Uint64Field(Field):
    """A 64-bit unsigned integer field."""

    def get_value(self, section, offset):
        return binary.unpack_uint64_from(section._data, offset)
