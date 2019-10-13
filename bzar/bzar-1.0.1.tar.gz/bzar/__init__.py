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

import os as _os
import io as _io
import pathlib as _pathlib
from collections import namedtuple as _namedtuple
import warnings as _warnings
import numpy as _np

from . import codec

VERSION_STR = "1.0.1"

try:
    from os import PathLike as _PathLike
except ImportError:
    _PathLike = str

BzarData     = _namedtuple('BzarData', ('data', 'metadata'))
DEFAULT_KEYS = ('shape', 'arrayorder') + codec.DATA_INFO_KEYS

def _read_exact(fileref, length):
    """returns the exact length of bytes or None"""
    arr = fileref.read(length)
    if len(arr) < length:
        return None
    else:
        return arr

def generate_metadata_dict(data=None, metadata=None, arrayorder='C'):
    """used internally to generate metadata dictionary from the data shape etc.
    and user-supplied metadata dict."""
    if data is None:
        raise ValueError("data cannot be None")
    metadict = dict(shape=data.shape, arrayorder=arrayorder)
    metadict.update(codec.encode_data_info(data))
    if metadata is not None:
        metadict.update(metadata)
    return metadict

def calc_metadata_size(metabin):
    """used internally to calculate the size of the binary metadata dictionary in bytes."""
    if not isinstance(metabin, bytes):
        metabin = codec.encode_metadata_dict(metabin)
    return len(metabin)

def check_suffix(fileref):
    """checks the suffix (extension) of `fileref` and
    add '.bzar' in case of none."""
    if isinstance(fileref, str):
        if len(_os.path.splitext(fileref)[1]) == 0:
            fileref += '.bzar'
    elif isinstance(fileref, bytes):
        if len(_os.path.splitext(fileref)[1]) == 0:
            fileref += b'.bzar'
    elif isinstance(fileref, _PathLike):
        fileref = _pathlib.Path(fileref)
        if len(fileref.suffix) == 0:
            fileref = fileref.with_suffix('.bzar')
    return fileref

def save(fileref, data=None, metadata=None, order='C'):
    """saves the data/metadata to a file represented by `fileref`."""
    if isinstance(fileref, (str, bytes, _PathLike)):
        fileref = check_suffix(fileref)
        with open(fileref, 'wb') as dest:
            save(dest, data=data, metadata=metadata, order=order)
        return

    # otherwise: assume fileref to be a IOBase
    if not isinstance(data, _np.ndarray):
        data = _np.array(data)
    metadict = generate_metadata_dict(data=data, metadata=metadata, arrayorder=order)
    metabin  = codec.encode_metadata_dict(metadict)
    metasiz  = calc_metadata_size(metabin)
    databin  = data.tobytes(order=order)
    fileref.write(databin)
    fileref.write(metabin)
    fileref.write(codec.encode_metadata_size(metasiz))

def read_data_sizes(fileref):
    """used internally to read the size of the data and the metadata dictionary
    in the file represented by `fileref`. returns a BzarData tuple."""
    if isinstance(fileref, (str, bytes, _PathLike)):
        with open(fileref, 'rb') as src:
            return read_data_sizes(src)

    # otherwise: assume fileref to be a BufferedReader
    if not fileref.seekable():
        raise ValueError(f"the file must be seekable: try reading from a normal file")
    width = codec.METADATA_SIZE_WIDTH
    fileref.seek(-width, _os.SEEK_END)
    metasiz_raw = _read_exact(fileref, width)
    if not metasiz_raw:
        raise codec.BzarDecodeError("failed to read the metadata size")
    metasiz = codec.decode_metadata_size(metasiz_raw)
    endofarray = fileref.seek(-(metasiz + width), _os.SEEK_END)
    datasiz = fileref.tell()
    return BzarData(datasiz, metasiz)

def read_metadata(fileref, complete=False, metadata_size=None):
    """reads and returns the metadta.
    if `complete` is set to True, it returns the non user-supplied metadata (e.g. data shape), too."""
    if isinstance(fileref, (str, bytes, _PathLike)):
        with open(fileref, 'rb') as src:
            return read_metadata(src, complete=complete, metadata_size=metadata_size)

    # otherwise: assume fileref to be a BufferedReader
    if not fileref.seekable():
        raise ValueError(f"the file must be seekable: try reading from a normal file")
    if metadata_size is None:
        _, metadata_size = read_data_sizes(fileref)
    fileref.seek(-(metadata_size + codec.METADATA_SIZE_WIDTH), _os.SEEK_END)
    metadict_raw = _read_exact(fileref, metadata_size)
    if not metadict_raw:
        raise codec.BzarDecodeError("failed to read the metadata dictionary")
    metadict = codec.decode_metadata_dict(metadict_raw)
    if complete == True:
        return metadict
    else:
        return get_user_supplied_metadata(metadict, copy=False)

def get_user_supplied_metadata(metadict, copy=True):
    """retrieves and returns the user-supplied metadata."""
    if copy == True:
        metadict = metadict.copy()
    for key in DEFAULT_KEYS:
        metadict.pop(key)
    return metadict

def load(fileref, with_metadata=False, complete_metadata=False, metadata_dict=None):
    """loads array data from the file represented by `fileref`, and returns it.
    if `with_metadata` is set to True, it returns the metadata, too,
    as a BzarData (data, metadata) tuple."""
    if isinstance(fileref, (str, bytes, _PathLike)):
        with open(fileref, 'rb') as src:
            return load(src, with_metadata=with_metadata,
                            complete_metadata=complete_metadata,
                            metadata_dict=metadata_dict)

    # otherwise: assume fileref to be a BufferedReader
    if not fileref.seekable():
        raise ValueError(f"the file must be seekable: try reading from a normal file")
    datasize, metasize = read_data_sizes(fileref)
    if metadata_dict is None:
        metadata_dict = read_metadata(fileref, complete=True, metadata_size=metasize)
    reshape = False
    if 'shape' not in metadata_dict.keys():
        _warnings.warn("the 'shape' key not found in metadata: a 1-D array is assumed.")
    else:
        reshape = True
    dtype    = codec.decode_data_info(metadata_dict)
    fileref.seek(0)
    data_raw = _read_exact(fileref, datasize)
    if data_raw is None:
        raise codec.BzarDecodeError("failed to read the binary data")
    data = _np.frombuffer(data_raw, dtype=dtype)
    if reshape == True:
        data = data.reshape(metadata_dict['shape'])

    if with_metadata == True:
        if complete_metadata == False:
            metadata_dict = get_user_supplied_metadata(metadata_dict)
        return BzarData(data, metadata_dict)
    else:
        return data
