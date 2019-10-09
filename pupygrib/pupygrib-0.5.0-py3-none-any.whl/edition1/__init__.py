"""An edition 1 GRIB message."""

import numpy

from pupygrib import base
from pupygrib import binary
from pupygrib import fields as basefields  # Python gets confused without alias
from pupygrib.edition1 import section1
from pupygrib.edition1 import section2
from pupygrib.edition1 import section3
from pupygrib.edition1 import section4


class IndicatorSection(base.Section):
    """The indicator section (0) of an edition 1 GRIB message."""

    identifier = basefields.BytesField(1, 4)
    totalLength = basefields.Uint24Field(5)
    editionNumber = basefields.Uint8Field(8)


class EndSection(base.Section):
    """The end section (5) of an edition 1 GRIB message."""

    endOfMessage = basefields.BytesField(1, 4)


class Message(base.Message):
    """An edition 1 GRIB message."""

    def get_coordinates(self):
        """Return the coordinates of this message's data points."""
        griddesc = self[2]
        if griddesc is None:
            raise NotImplementedError("pupygrib does not support catalogued grids")
        return griddesc._get_coordinates()

    def get_values(self):
        """Return the data values of this message."""
        values = self[4]._unpack_values()
        values = self[1]._scale_values(values)
        bitmapdesc = self[3]
        if bitmapdesc:
            mask = ~numpy.array(bitmapdesc.bitmap, dtype=bool)
            mvalues = numpy.empty(len(mask), dtype=float)
            mvalues[~mask] = values
            values = numpy.ma.array(mvalues, mask=mask)
        griddesc = self[2]
        if griddesc:
            values = griddesc._order_values(values)
        return values

    def _get_section0(self):
        return IndicatorSection(self._data, 0, 8)

    def _get_section1(self):
        offset = self[0].end
        length = binary.unpack_uint24_from(self._data, offset)
        return section1.get_section(self._data, offset, length)

    def _get_section2(self):
        proddef = self[1]
        if not proddef.section1Flags & 0x80:
            return None

        offset = proddef.end
        length = binary.unpack_uint24_from(self._data, offset)
        return section2.get_section(self._data, offset, length)

    def _get_section3(self):
        proddef = self[1]
        if not proddef.section1Flags & 0x40:
            return None

        offset = (self[2] or proddef).end
        length = binary.unpack_uint24_from(self._data, offset)
        return section3.BitMapSection(self._data, offset, length)

    def _get_section4(self):
        offset = (self[3] or self[2] or self[1]).end
        length = binary.unpack_uint24_from(self._data, offset)
        return section4.get_section(self._data, offset, length)

    def _get_section5(self):
        return EndSection(self._data, self[4].end, 4)
