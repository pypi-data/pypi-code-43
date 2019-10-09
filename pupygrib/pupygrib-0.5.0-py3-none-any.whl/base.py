"""Base classes for GRIB messages of edition 1 and 2."""

import itertools

from pupygrib.fields import Field


class SectionMeta(type):
    """Meta class for GRIB message sections.

    This meta class automatically assign names to fields from the
    attribute name they are given on the class.  It is also
    responsible for assigning the fieldnames property to sections.

    """

    def __init__(cls, name, bases, namespace, **kwargs):
        fieldnames = set(
            itertools.chain.from_iterable(
                base.fieldnames for base in bases if hasattr(base, "fieldnames")
            )
        )
        for key, value in namespace.items():
            if isinstance(value, Field):
                value.name = key
                fieldnames.add(key)
        cls.fieldnames = fieldnames


class Section(metaclass=SectionMeta):
    """Base class for sections of GRIB messages.

    The *data* argument should be a memoryview of the whole GRIB
    message.  *offset* and *length* gives the slice that belongs to
    this section of that view.

    """

    def __init__(self, data, offset, length):
        self.offset = offset
        self.end = offset + length
        self._data = data[self.offset : self.end]


class Message:
    """Base class for GRIB messages of edition 1 and 2.

    The *data* argument should be a bytes-like object containing the
    whole GRIB message.

    """

    def __init__(self, data, filename=None):
        self.filename = filename
        self._data = memoryview(data)
        self._sections = {}

    def __getitem__(self, index):
        """Return a section of the GRIB message with the given *index*.

        If *index* is a valid section for the current GRIB edition but
        not included in the message, None is returned.

        """
        try:
            return self._sections[index]
        except KeyError:
            try:
                getter = getattr(self, f"_get_section{index}")
            except AttributeError:
                raise IndexError("no such section")
            self._sections[index] = section = getter()
            return section
