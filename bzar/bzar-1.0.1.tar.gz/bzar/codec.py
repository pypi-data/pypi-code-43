#
# MIT License
#
# Copyright (c) 2019 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""functions related to encoding/decoding of data and metadata."""

import sys as _sys
import json as _json
import struct as _struct
import warnings as _warnings

import numpy as _np

SizeEncoder         = _struct.Struct('Q')
METADATA_SIZE_WIDTH = 8
DATA_INFO_KEYS      = ('datatype', 'byteorder')

DtypeDecoder        = {
    'byte':    (_np.ubyte,   False),
    'bool8':   (_np.bool,    False),
    'int8':    (_np.int8,    False),
    'uint8':   (_np.uint8,   False),
    'int16':   (_np.int16,   True),
    'uint16':  (_np.uint16,  True),
    'int32':   (_np.int32,   True),
    'uint32':  (_np.uint32,  True),
    'int64':   (_np.int64,   True),
    'uint64':  (_np.uint64,  True),
    'float32': (_np.float32, False),
    'float64': (_np.float64, False)
}
ByteOrderDecoder    = {
    'little': '<',
    'big':    '>'
}

class BzarDecodeError(IOError):
    def __init__(self, msg):
        super().__init__(msg)

def encode_byteorder(dtype):
    """used internally to resolve the byte order."""
    order = dtype.byteorder
    if order in ('@', '='):
        return _sys.byteorder # 'little' or 'big'
    elif order == '<':
        return 'little'
    elif order in ('>', '!'):
        return 'big'
    else:
        raise ValueError(f"unknown endian-ness: {order}")

def encode_data_info(data):
    """returns information about the data array as a dict."""
    dtype = data.dtype
    datatype = None

    if dtype.char == 'c':
        datatype  = 'byte'
        order     = 'NA'

    elif dtype.char == 'b':
        datatype  = 'int8'
        order     = 'NA'

    elif dtype.char == 'B':
        datatype  = 'uint8'
        order     = 'NA'

    elif dtype.char == '?':
        datatype  = 'bool8'
        order     = 'NA'

    elif dtype.char == 'h':
        datatype  = 'int16'
        order     = encode_byteorder(dtype)

    elif dtype.char == 'H':
        datatype  = 'uint16'
        order     = encode_byteorder(dtype)

    elif dtype.char in ('i', 'l'):
        datatype  = f'int{dtype.itemsize*8}'
        order     = encode_byteorder(dtype)

    elif dtype.char in ('I', 'L'):
        datatype  = f'uint{dtype.itemsize*8}'
        order     = encode_byteorder(dtype)

    elif dtype.char == 'q':
        datatype  = 'int64'
        order     = encode_byteorder(dtype)

    elif dtype.char == 'Q':
        datatype  = 'uint64'
        order     = encode_byteorder(dtype)

    elif dtype.char == 'f':
        datatype  = 'float32'
        order     = 'NA'

    elif dtype.char == 'd':
        datatype  = 'float64'
        order     = 'NA'

    if datatype is None:
        raise ValueError(f"unsupported data type: {str(dtype)}")
    return dict(datatype=datatype, byteorder=order)

def decode_data_info(metadict):
    """used internally to generate 'dtype' object from the metadata dictionary."""
    if 'datatype' not in metadict.keys():
        raise KeyError(f"'datatype' not found in the metadata dictionary")
    datatype = metadict['datatype']
    if datatype not in DtypeDecoder.keys():
        raise KeyError(f"unknown data type: {datatype}")
    basetype, byteorder_sensitive = DtypeDecoder[datatype]
    if byteorder_sensitive == True:
        baseorder = _sys.byteorder
        if 'byteorder' not in metadict.keys():
            _warnings.warn("'byteorder' not found in the metadata dictionary: the native order is assumed.")
            return basetype
        order = metadict['byteorder']
        if order != baseorder:
            return basetype.newbyteorder(ByteOrderDecoder[order])
        else:
            return basetype
    else:
        return basetype

def encode_metadata_dict(metadict):
    """used internally to encode the metadata dictionary into its binary format."""
    return _json.dumps(metadict, separators=(',', ':')).encode('ascii')

def decode_metadata_dict(rawbytes):
    """used internally to decode the metadata dictionary from its binary format."""
    metadict = _json.loads(rawbytes.decode('ascii'))
    for key, val in metadict.items():
        if isinstance(val, list):
            metadict[key] = tuple(val)
    return metadict

def encode_metadata_size(metasiz):
    """used internally to encode the size of the metadata dictionary."""
    return SizeEncoder.pack(metasiz)

def decode_metadata_size(binarray):
    """used internally to decode the size of the metadata dictionary."""
    return SizeEncoder.unpack(binarray)[0]
