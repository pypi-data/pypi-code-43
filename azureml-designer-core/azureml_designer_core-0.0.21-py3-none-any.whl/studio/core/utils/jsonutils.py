import json
import os

from azureml.studio.core.utils.fileutils import ensure_folder

INDENT = 2


def dump_to_json(obj, stream, indent=INDENT, sort_keys=False):
    json.dump(obj, stream, indent=indent, sort_keys=sort_keys)


def dump_to_json_file(obj, filename, indent=INDENT, sort_keys=False):
    ensure_folder(os.path.dirname(os.path.abspath(filename)))
    with open(filename, 'w') as fout:
        dump_to_json(obj, fout, indent=indent, sort_keys=sort_keys)


def load_json(stream):
    return json.load(stream)


def load_json_file(filename):
    with open(filename, 'r') as fin:
        return load_json(fin)


JSON_TYPES = {int, float, str, bool, type(None), dict, list}


def json_equals(data1, data2, precision=0):
    """
    Compare two json objects at a certain precision threshold to avoid floating number precision error.

    >>> data1 = {'floatval': 1.0010}
    >>> data2 = {'floatval': 1.0014}
    >>> json_equals(data1, data2)
    False
    >>> json_equals(data1, data2, 0.001)
    True
    """
    if not type(data1) in JSON_TYPES:
        raise TypeError(f"Object of type {data1.__class__.__name__} is not JSON serializable")
    if not type(data2) in JSON_TYPES:
        raise TypeError(f"Object of type {data2.__class__.__name__} is not JSON serializable")

    # Both int and float are "number type" in json
    if type(data1) != type(data2) and {type(data1), type(data2)} != {float, int}:
        return False

    if isinstance(data1, list):
        if len(data1) != len(data2):
            return False
        for item1, item2 in zip(data1, data2):
            if not json_equals(item1, item2, precision):
                return False

    elif isinstance(data1, dict):
        if len(data1) != len(data2):
            return False
        for k, item1 in data1.items():
            if k not in data2:
                return False
            if not json_equals(item1, data2[k], precision):
                return False

    elif data1 is None or isinstance(data1, (str, bool)):
        return data1 == data2

    # Comparing numbers
    else:
        return abs(data1 - data2) <= precision

    return True
