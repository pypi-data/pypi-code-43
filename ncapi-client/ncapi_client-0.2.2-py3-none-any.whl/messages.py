"""
 NEURAL CONCEPT CONFIDENTIAL
 __________________
 
  [2018] Neural Concept SA-SARL, Lausanne, Switzerland
  All Rights Reserved.
 
 If you are reading this NOTICE as a result of a de-obfuscation
 or a reverse Engineering of Neural Concept’s software, you are likely
 breaking Neural Concept Shape’s End-User Licence Agreement. 
 Please contact Neural Concept Sarl without any delay.

 NOTICE:  All information contained herein is, and remains
 the property of Neural Concept and its suppliers,
 if any.  The intellectual and technical concepts contained
 herein are proprietary to Neural Concept
 and its suppliers and may be covered by European and Foreign Patents,
 patents in process, and are protected by trade secret or copyright law.
 Dissemination or usage of this information or reproduction of this material
 is strictly forbidden unless prior written permission is obtained
 from Neural Concept.
 Usage of file or code is subject to the terms and conditions defined in
 Neural Concept Shape’s End-User Licence Agreement.
""" 

# a tiny messaging library
import json
import numpy as np

BYTE_ORDER = "big"
# number of bytes for the message type
HEADER_NBYTES = 4
# number of bytes for the array sizes
SIZE_NBYTES = 4

# low-level message types
MSG_INT32 = 0
MSG_STRING = 1
MSG_JSON = 2
MSG_ARRAY = 3
MSG_MULTIPART = 10

# { mesh stuff
# requests
MSG_GET_MESH = 20
MSG_SET_MESH_BY_ID = 21
MSG_SET_MESH = 22
# MSG_GET_MESH_PART = 22
# data
MSG_MESH_VERTS = 30
MSG_MESH_FIELD = 31
MSG_MESH = 32
# MSG_MESH_PART = 33
# } mesh stuff

# { pred stuff
# requests
MSG_GET_PREDICTION = 40
MSG_GET_PREDICTION_FIELD = 41
MSG_GET_PREDICTION_SCALARS = 42
# scalars
MSG_PREDICTION = 50
MSG_PREDICTION_FIELD = 51
MSG_PREDICTION_SCALARS = 52
# } pred stuff

# { deformation stuff
# requests
MSG_APPLY_DEFORMATION = 60
# } deformation stuff

# { model stuff
MSG_GET_MODEL = 80
MSG_SET_MODEL_BY_ID = 81
MSG_MODEL = 90
# } model stuff

# { error stuff
MSG_OK = 69
MSG_ERROR = 70
MSG_WARN = 71
# } error stuff

# vector-like formats
MSG_FLOAT32_TYPE = 100
MSG_INT32_TYPE = 101
MSG_FLOAT64_TYPE = 102
MSG_INT64_TYPE = 103

MSG_VECTOR_TYPE = 200
MSG_MATRIX_TYPE = 201


def msg_header(msg_type):
    return msg_type.to_bytes(HEADER_NBYTES, BYTE_ORDER)


def _btype(msg_type):
    return msg_type.to_bytes(HEADER_NBYTES, BYTE_ORDER)


def _bsize(size):
    assert isinstance(size, int)
    return size.to_bytes(SIZE_NBYTES, BYTE_ORDER)


def _bshape(shape):
    assert len(shape) >= 1
    return _bsize(len(shape)) + b"".join(_bsize(d) for d in shape)


def seq2dict(args):
    return {k: v for k, v in zip(args[0::2], args[1::2])}


def dict2seq(d):
    return sum(((k, v) for k, v in d.items()), ())


def msg_string(value):
    return msg_header(MSG_STRING) + value.encode()


def msg_json(value):
    return msg_header(MSG_JSON) + json.dumps(value).encode()


def msg_mesh_verts(verts):
    assert verts.dtype == np.float32
    return msg_header(MSG_MESH_VERTS) + verts.tobytes()


def msg_mesh_field(field):
    assert field.dtype == np.float32
    return msg_header(MSG_MESH_FIELD) + field.tobytes()


def msg_array(arr):
    if arr.dtype == np.float32:
        val_type = MSG_FLOAT32_TYPE
    elif arr.dtype == np.float64:
        val_type = MSG_FLOAT64_TYPE
    elif arr.dtype == np.int32:
        val_type = MSG_INT32_TYPE
    elif arr.dtype == np.int64:
        val_type = MSG_INT64_TYPE
    else:
        raise NotImplementedError(f"unsupported dtype {arr.dtype}")
    return (
        _btype(MSG_ARRAY) + _btype(val_type) + _bshape(arr.shape) + arr.data.tobytes()
    )


def msg_parse_array(msg_bytes):
    i = HEADER_NBYTES
    val_type = int.from_bytes(msg_bytes[i : i + SIZE_NBYTES], BYTE_ORDER)
    if val_type == MSG_FLOAT32_TYPE:
        dtype = np.float32
    elif val_type == MSG_INT32_TYPE:
        dtype = np.int32
    elif val_type == MSG_FLOAT64_TYPE:
        dtype = np.float64
    elif val_type == MSG_INT64_TYPE:
        dtype = np.int64
    else:
        raise NotImplementedError(f"unknown value_type: {val_type}")
    i += SIZE_NBYTES
    num_dims = int.from_bytes(msg_bytes[i : i + SIZE_NBYTES], BYTE_ORDER)
    i += SIZE_NBYTES
    shape = []
    for d in range(num_dims):
        shape.append(int.from_bytes(msg_bytes[i : i + SIZE_NBYTES], BYTE_ORDER))
        i += SIZE_NBYTES
    # return np.fromstring(msg_bytes[i:], dtype=dtype).reshape(shape)
    return np.frombuffer(msg_bytes[i:], dtype=dtype).reshape(shape)


def msg_multipart(*values):
    msg = _btype(MSG_MULTIPART) + _bsize(len(values))
    for value in values:
        if isinstance(value, int):
            part = _btype(MSG_INT32) + _bsize(value)
        elif isinstance(value, str):
            part = msg_string(value)
        elif isinstance(value, np.ndarray):
            part = msg_array(value)
        else:
            raise NotImplementedError(str(type(value)))
        msg += _bsize(len(part)) + part
    return msg


def msg_parse_multipart(msg_bytes, with_headers=False):
    parts = []
    i = HEADER_NBYTES
    num_parts = int.from_bytes(msg_bytes[i : i + SIZE_NBYTES], BYTE_ORDER)
    i += SIZE_NBYTES
    for p in range(num_parts):
        part_size = int.from_bytes(msg_bytes[i : i + SIZE_NBYTES], BYTE_ORDER)
        i += SIZE_NBYTES
        header, body = msg_parse(msg_bytes[i : i + part_size])
        i += part_size
        if with_headers:
            parts.append((header, body))
        else:
            parts.append(body)
    return parts


def msg_parse(msg_bytes):
    """
    Parsing the raw message bytes and produces python-compatible
    object (NumPy array or string)
    """
    header = int.from_bytes(msg_bytes[:HEADER_NBYTES], BYTE_ORDER)
    if header == MSG_INT32:
        return header, int.from_bytes(msg_bytes[HEADER_NBYTES:], BYTE_ORDER)
    elif header == MSG_STRING:
        return header, msg_bytes[HEADER_NBYTES:].decode()
    elif header == MSG_JSON:
        return header, json.loads(msg_bytes[HEADER_NBYTES:].decode())
    elif header == MSG_ARRAY:
        return header, msg_parse_array(msg_bytes)
    elif header == MSG_MULTIPART:
        return header, msg_parse_multipart(msg_bytes)
    else:
        raise NotImplementedError()
