"""
Package for working with JSON/JSONSchema in an object-oriented manner.
"""
from ._BasicSchemaValidator import BasicSchemaValidator
from ._deep_copy import deep_copy
from ._error import JSONError
from ._typing import RawJSONElement, RawJSONNumber, RawJSONArray, RawJSONObject, RawJSONPrimitive, \
    is_raw_json_primitive, is_raw_json_null, is_raw_json_number, is_raw_json_object, is_raw_json_array, \
    is_raw_json_element, is_raw_json_element_type
