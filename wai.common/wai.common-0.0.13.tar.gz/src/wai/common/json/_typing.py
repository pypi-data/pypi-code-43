"""
Typing functionality and static types for JSON package.
"""
from typing import Dict, Union, List, Any, Set

from ..iterate import all_meet_predicate

# The type of a raw JSON object in Python-land
RawJSONObject = Dict[str, 'RawJSONElement']

# The type of a raw JSON array in Python-land
RawJSONArray = List['RawJSONElement']

# The type of an arbitrary raw JSON number in Python-land
RawJSONNumber = Union[int, float]

# The type of a raw JSON primitive
RawJSONPrimitive = Union[RawJSONNumber, str, bool, None]

# The type of an arbitrary raw JSON element in Python-land
RawJSONElement = \
    Union[
        RawJSONObject,  # Object
        RawJSONArray,  # Array
        str,  # String
        RawJSONNumber,  # Number (real/integer)
        bool,  # True/false
        None  # Null
    ]

# The types of raw JSON elements
RAW_JSON_ELEMENT_TYPES: Set[type] = {dict, list, float, int, str, bool, None}


def is_raw_json_object(py_obj: Any) -> bool:
    """
    Checks if the given Python object is a raw JSON object.

    :param py_obj:  The Python object to check.
    :return:        True if the Python object is a raw JSON object,
                    False if not.
    """
    # Must be a dictionary
    if not isinstance(py_obj, dict):
        return False

    # All keys must be strings
    if not all(isinstance(key, str) for key in py_obj.keys()):
        return False

    # All values must be raw JSON elements
    if not all_meet_predicate(py_obj.values(), is_raw_json_element):
        return False

    # All checks passed
    return True


def is_raw_json_array(py_obj: Any) -> bool:
    """
    Checks if the given Python object is a raw JSON array.

    :param py_obj:  The Python object to check.
    :return:        True if the Python object is a raw JSON array,
                    False if not.
    """
    # Must be a list
    if not isinstance(py_obj, list):
        return False

    # All elements must be raw JSON elements
    if not all_meet_predicate(py_obj, is_raw_json_element):
        return False

    # All checks passed
    return True


def is_raw_json_number(py_obj: Any) -> bool:
    """
    Checks if the given Python object is a raw JSON number.

    :param py_obj:  The Python object to check.
    :return:        True if the Python object is a raw JSON number,
                    False if not.
    """
    # Must be an int or a float
    return isinstance(py_obj, int) or isinstance(py_obj, float)


def is_raw_json_null(py_obj: Any) -> bool:
    """
    Checks if the given Python object is a raw JSON null.

    :param py_obj:  The Python object to check.
    :return:        True if the Python object is a raw JSON null,
                    False if not.
    """
    # Must be None
    return py_obj is None


def is_raw_json_primitive(py_obj: Any) -> bool:
    """
    Checks if the given Python object is a raw JSON primitive.

    :param py_obj:  The Python object to check.
    :return:        True if the Python object is a raw JSON primitive,
                    False if not.
    """
    # Must be a number, string, bool or null
    return \
        is_raw_json_number(py_obj) or \
        isinstance(py_obj, str) or \
        isinstance(py_obj, bool) or \
        is_raw_json_null(py_obj)


def is_raw_json_element(py_obj: Any) -> bool:
    """
    Checks if the given Python object is any raw JSON element.

    :param py_obj:  The Python object to check.
    :return:        True if the Python object is a raw JSON element,
                    False if not.
    """
    return \
        is_raw_json_primitive(py_obj) or \
        is_raw_json_array(py_obj) or \
        is_raw_json_object(py_obj)


def is_raw_json_element_type(py_type: type) -> bool:
    """
    Checks if the given type is a raw JSON primitive type.

    :param py_type:     The type to check.
    :return:            True if the type is a raw JSON primitive type,
                        False if not.
    """
    return py_type in RAW_JSON_ELEMENT_TYPES
