"""
Module for static and dynamic typing of JSON schema.
"""
from typing import Union, Dict

import jsonschema

from ...meta import does_not_raise
from .._typing import RawJSONObject

# The type of a schema (boolean schema are trivial)
JSONSchema = Union[RawJSONObject, bool]

# The type of a definition
JSONDefinitions = Dict[str, JSONSchema]


def is_schema(schema):
    """
    Checks if the given object is a valid schema.

    :param schema:  The schema to check.
    :return:        True if it is a schema,
                    False if not.
    """
    # Get JSONSchema to check the schema against the latest standard
    return does_not_raise(jsonschema.validators.validator_for(schema).check_schema(schema))
