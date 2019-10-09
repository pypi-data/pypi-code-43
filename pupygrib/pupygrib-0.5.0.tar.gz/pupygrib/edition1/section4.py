"""Binary data sections of GRIB edition 1."""

import numpy

from pupygrib import base
from pupygrib import fields
from pupygrib.edition1.fields import FloatField


class BinaryDataSection(base.Section):
    """The binary data section (4) of an edition 1 GRIB message."""

    section4Length = fields.Uint24Field(1)
    dataFlag = fields.Uint8Field(4)
    binaryScaleFactor = fields.Int16Field(5)
    referenceValue = fields.BytesField(7, 4)
    bitsPerValue = fields.Uint8Field(11)
    values = fields.BytesField(12)

    def _unpack_values(self):
        raise NotImplementedError("pupygrib does not support the current packing")


class SimpleGridDataField(base.Field):
    """Simply packed grid-point data values."""

    def get_value(self, section, offset):
        bits_per_value = section.bitsPerValue
        if bits_per_value == 0:
            return None
        num_bytes, extra_bits = divmod(bits_per_value, 8)
        if bits_per_value not in (8, 12, 16, 32, 64):
            raise NotImplementedError(
                f"pupygrib does not support {bits_per_value} bits per value"
            )

        unused_bytes = -(section.dataFlag & 0x0F) // 8 or None
        dtype = numpy.dtype(">u{}".format(num_bytes if extra_bits == 0 else 1))
        buf = section._data[offset:unused_bytes]
        data = numpy.frombuffer(buf, dtype=dtype)
        if extra_bits > 0:
            data = read_uint12(data)

        return data


def read_uint12(data):
    # https://stackoverflow.com/questions/44735756/python-reading-12-bit-binary-files
    fst_uint8, mid_uint8, lst_uint8 = (
        numpy.reshape(data, (data.shape[0] // 3, 3)).astype(numpy.uint16).T
    )
    fst_uint12 = (fst_uint8 << 4) + (mid_uint8 >> 4)
    snd_uint12 = ((mid_uint8 % 16) << 8) + lst_uint8
    return numpy.reshape(
        numpy.concatenate((fst_uint12[:, None], snd_uint12[:, None]), axis=1),
        2 * fst_uint12.shape[0],
    )


class SimpleGridDataSection(BinaryDataSection):
    """A simply packed grid-point data section (4) of GRIB edition 1."""

    referenceValue = FloatField(7)
    values = SimpleGridDataField(12)

    def _unpack_values(self):
        values = 0 if self.values is None else self.values.astype(float)
        return self.referenceValue + values * 2.0 ** self.binaryScaleFactor


def get_section(buf, offset, length):
    """Return a new section 4 of the correct type from *buf* at *offset*."""
    datadesc = BinaryDataSection(buf, offset, length)
    try:
        sectionclass = {0x00: SimpleGridDataSection}[datadesc.dataFlag & 0xF0]
    except KeyError:
        return datadesc
    else:
        return sectionclass(buf, offset, length)
