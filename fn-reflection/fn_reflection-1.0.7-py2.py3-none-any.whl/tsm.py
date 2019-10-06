# parser library for tsm file (internal data format of influxDB)
from io import SEEK_END, SEEK_CUR
from struct import Struct
from collections import namedtuple

TSMHeader = namedtuple('TSMHeader', ('magic', 'version'))


def read_tsm(filename):
    with open(filename, 'rb') as stream:
        return read_tsm_stream(stream)


def read_tsm_stream(stream):
    stream.seek(0)
    tsm_header = _read_header(stream)
    index_offset = _get_offset(stream)
    index = read_index(stream, index_offset)
    return index


def size(stream):
    current_pos = stream.tell()
    stream.seek(0, SEEK_END)
    stream_size = stream.tell()
    stream.seek(current_pos)
    return stream_size


def read_u1(stream):
    return Struct('B').unpack(stream.read(1))[0]


def read_u2be(stream):
    return Struct('>H').unpack(stream.read(2))[0]


def read_u4be(stream):
    return Struct('>I').unpack(stream.read(4))[0]


def read_u8be(stream):
    return Struct('>Q').unpack(stream.read(8))[0]


def ensure(stream, expected):
    actual = stream.read(len(expected))
    assert actual == expected
    return actual


def _read_header(stream):
    magic = ensure(stream, b"\x16\xD1\x16\xD1")
    version = read_u1(stream)
    return TSMHeader(magic=magic, version=version)


def _get_offset(stream):
    pos = stream.tell()
    stream.seek(size(stream) - 8)
    offset = read_u8be(stream)
    stream.seek(pos)
    return offset


def read_index(stream, index_offset):
    stream.seek(index_offset)
    entries = []
    i = 0
    while not stream.tell() >= size(stream) - 8:
        item = read_index_header(stream)
        entries.append(item)
        i += 1
    stream.seek(0)
    return entries


def read_index_header(stream):
    key_len = read_u2be(stream)
    key = (stream.read(key_len))
    _type = read_u1(stream)
    entry_count = read_u2be(stream)
    index_entries = []
    for i in range(entry_count):
        index_entry = read_index_entry(stream)
        index_entries.append(index_entries)
    return (key, _type, index_entries)


def read_index_entry(stream):
    min_time = read_u8be(stream)
    max_time = read_u8be(stream)
    block_offset = read_u8be(stream)
    block_size = read_u4be(stream)
    _pos = stream.tell()
    stream.seek(block_offset)
    crc32 = read_u4be(stream)
    payload = stream.read(block_size - 4)
    stream.seek(_pos)
    return (min_time, max_time, payload)
