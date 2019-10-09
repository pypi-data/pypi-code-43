"""A light-weight pure Python GRIB reader."""

import io
from itertools import repeat, takewhile

import pkg_resources

from pupygrib import binary
from pupygrib import edition1
from pupygrib import edition2
from pupygrib.exceptions import ParseError

__version__ = pkg_resources.get_distribution("pupygrib").version


def _strip_zeros(stream):
    # Remove up to 64 leading zeros from *stream*.
    stream.seek(-len(stream.read(64).lstrip(b"\0")), io.SEEK_CUR)


def _try_read_message(stream):
    # Try to read one GRIB message from *stream*.  If end-of-file is
    # encountered immediately, return None.  If end-of-file is reached
    # while parsing the message or if the parsing fails for some other
    # reason, a ParseError is raised.

    # Check that we have a GRIB message
    startpos = stream.tell()
    magic = stream.read(4)
    if not magic:
        return None
    if magic != b"GRIB":
        # Some GRIB files seem to be padded with zeros between the
        # messages. We allow this.
        _strip_zeros(stream)
        startpos = stream.tell()
        magic = stream.read(4)
        if magic != b"GRIB":
            raise ParseError("not a GRIB message")

    # Find the edition and length
    header = binary.checkread(stream, 4)
    edition = binary.unpack_uint8_from(header, 3)
    if edition == 1:
        length = binary.unpack_uint24_from(header)
        message_class = edition1.Message
    elif edition == 2:
        length = binary.unpack_uint64_from(binary.checkread(stream, 8))
        message_class = edition2.Message
    else:
        raise ParseError("unknown edition number '{}'".format(edition))

    # Read and check the end of the message
    stream.seek(startpos)
    data = binary.checkread(stream, length)
    if data[-4:] != b"7777":
        raise ParseError("end-of-message marker not found")

    # Create and return the message instance
    return message_class(data, getattr(stream, "name", None))


def read(stream):
    """Iterate over a GRIB file's messages.

    *stream* should be a readable binary file-like object that supports
    random access.  The easiest way to obtain such an object is simply
    to use the built-in open() function with mode set to 'rb'.

    """
    return takewhile(lambda msg: msg, map(_try_read_message, repeat(stream)))
