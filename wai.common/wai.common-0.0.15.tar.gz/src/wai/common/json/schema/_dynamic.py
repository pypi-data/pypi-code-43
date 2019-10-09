"""
Methods for creating some common JSON-validation schema,
based on some parameters.
"""
from typing import Dict, Set, Optional, Union

from ._error import JSONSchemaError
from ._typing import JSONSchema
from .._typing import RawJSONNumber, RawJSONPrimitive
from .constants import *
from ._definitions import consolidate_definitions, JSONDefinitions
from .._deep_copy import deep_copy


def string_schema(min_length: Optional[int] = None,
                  max_length: Optional[int] = None,
                  pattern: Optional[str] = None,
                  format: Optional[str] = None) -> JSONSchema:
    """
    Creates a schema which validates a string.

    TODO: Format strings are only optionally enforced by validators. Add check
          to ensure that the given format string will be enforced, and possibly
          a flag to skip this check if unnecessary.

    :param min_length:  The minimum length of the string.
    :param max_length:  The maximum length of the string.
    :param pattern:     A regex to validate against.
    :param format:      The format type to validate against.
    :return:            The schema.
    """
    # Create the base schema
    schema: JSONSchema = {
        TYPE_KEYWORD: STRING_TYPE
    }

    # Add the minimum length if given
    if min_length is not None:
        if min_length < 0:
            raise ValueError(f"min_length must be non-negative if given, got {min_length}")
        schema[MIN_LENGTH_KEYWORD] = min_length

    # Add the maximum length if given
    if max_length is not None:
        if max_length < 0:
            raise ValueError(f"max_length must be non-negative if given, got {max_length}")
        schema[MAX_LENGTH_KEYWORD] = max_length

    # Add the pattern if given
    if pattern is not None:
        schema[PATTERN_KEYWORD] = pattern

    # Add the format if given
    if format is not None:
        schema[FORMAT_KEYWORD] = format

    return schema


def standard_object(required_properties: Optional[Dict[str, JSONSchema]] = None,
                    optional_properties: Optional[Dict[str, JSONSchema]] = None,
                    additional_properties: Union[JSONSchema, bool] = False) -> JSONSchema:
    """
    Creates an schema which validates an object.

    :param required_properties:             The required properties.
    :param optional_properties:             The optional properties.
    :param additional_properties:           Either a schema for validating any additional properties,
                                            or a boolean specifying whether additional properties are allowed.
    :return:                                The schema.
    """
    # Set the default properties if none are provided
    if required_properties is None:
        required_properties = {}
    if optional_properties is None:
        optional_properties = {}

    # Make sure there are not duplicate properties between required and optional.
    for key in required_properties:
        if key in optional_properties:
            raise JSONSchemaError(f"Property '{key}' can't be both required and optional")

    # Copy all schema
    required_properties = deep_copy(required_properties)
    optional_properties = deep_copy(optional_properties)
    additional_properties = deep_copy(additional_properties)

    # Extract any definitions
    definitions: JSONDefinitions = consolidate_definitions(*required_properties.values(),
                                                           *optional_properties.values(),
                                                           additional_properties,
                                                           pop=True)

    # Combine the required and optional properties
    combined_properties = {}
    combined_properties.update(required_properties)
    combined_properties.update(optional_properties)

    # Create the schema
    schema = {
        TYPE_KEYWORD: OBJECT_TYPE,
        PROPERTIES_KEYWORD: combined_properties,
        DEFINITIONS_KEYWORD: definitions
    }

    # Add the list of required properties if there are any
    if len(required_properties) > 0:
        schema[REQUIRED_PROPERTIES_KEYWORD] = list(required_properties.keys())

    # Disallow additional properties if not selected
    if additional_properties is not True:
        schema[ADDITIONAL_PROPERTIES_KEYWORD] = additional_properties

    return schema


def constant(value: RawJSONPrimitive) -> JSONSchema:
    """
    Creates a schema that only validates a constant value.

    :param value:   The constant value.
    :return:        The schema.
    """
    return {CONSTANT_KEYWORD: value}


def enum(*values: RawJSONPrimitive) -> JSONSchema:
    """
    Creates a schema that only validates a fixed set of values.

    :param values:  The set of allowed values.
    :return:        The schema.
    """
    unique_values: Set[RawJSONPrimitive] = set(values)

    return {ENUMERATION_KEYWORD: list(unique_values)}


def number(minimum: Optional[RawJSONNumber] = None,
           maximum: Optional[RawJSONNumber] = None,
           integer_only: bool = False,
           multiple_of: Optional[RawJSONNumber] = None,
           exclusive_minimum: bool = False,
           exclusive_maximum: bool = False) -> JSONSchema:
    """
    Creates a schema that validates a numeric value.

    :param minimum:             The minimum value the number must take.
    :param maximum:             The maximum value the number must take.
    :param integer_only:        Whether to only accept integer values.
    :param multiple_of:         The number the value must be a multiple of.
    :param exclusive_minimum:   Whether the minimum value is exclusive.
    :param exclusive_maximum:   Whether the maximum value is exclusive.
    :return:                    The schema.
    """
    # Create the schema with the correct type
    schema: JSONSchema = {
        TYPE_KEYWORD: NUMBER_TYPE if not integer_only else INTEGER_TYPE
    }

    # Set the minimum if supplied
    if minimum is not None:
        schema[MINIMUM_KEYWORD if not exclusive_minimum else EXCLUSIVE_MINIMUM_KEYWORD] = minimum

    # Set the maximum if supplied
    if maximum is not None:
        schema[MAXIMUM_KEYWORD if not exclusive_maximum else EXCLUSIVE_MAXIMUM_KEYWORD] = maximum

    # Set the multiple if supplied
    if multiple_of is not None:
        schema[MULTIPLE_OF_KEYWORD] = multiple_of

    return schema


def regular_array(element_schema: JSONSchema,
                  min_elements: int = 0,
                  max_elements: Optional[int] = None,
                  unique_elements: bool = False) -> JSONSchema:
    """
    Creates a schema validating an array of items of the same type.

    :param element_schema:  The schema to validate each item.
    :param min_elements:    The minimum number of elements that must be in the array.
    :param max_elements:    The maximum number of elements that must be in the array.
    :param unique_elements: Whether the elements of the array must be distinct.
    :return:                The schema.
    """
    # It's invalid to provided a negative value for an element count restriction
    if min_elements < 0 or (max_elements is not None and max_elements < 0):
        raise JSONSchemaError("Can't have an array with a negative number of elements")

    # Can't have a maximum less than a minimum
    if max_elements is not None and max_elements < min_elements:
        raise JSONSchemaError("max_elements can't be less than min_elements")

    # Copy the element schema
    element_schema = deep_copy(element_schema)

    # Extract any definitions
    definitions: JSONDefinitions = consolidate_definitions(element_schema, pop=True)

    # Create the schema with the array type and element schema
    schema: JSONSchema = {
        TYPE_KEYWORD: ARRAY_TYPE,
        ITEMS_KEYWORD: element_schema,
        DEFINITIONS_KEYWORD: definitions
    }

    # Add the minimum length if more than nothing
    if min_elements > 0:
        schema[MIN_ITEMS_KEYWORD] = min_elements

    # Add the maximum length if present
    if max_elements is not None:
        schema[MAX_ITEMS_KEYWORD] = max_elements

    # Add the uniqueness flag if set
    if unique_elements:
        schema[UNIQUE_ITEMS_KEYWORD] = True

    return schema


def one_of(*schema: JSONSchema) -> JSONSchema:
    """
    Creates a schema which makes sure the value matches only one of the
    given schema.

    :param schema:  The individual schema.
    :return:        The combined schema.
    """
    # Must provide at least 2 schema
    if len(schema) < 2:
        raise JSONSchemaError("Can't use one_of with fewer than 2 sub-schema")

    # Copy the schema into a list
    schema = deep_copy(list(schema))

    # Extract any definitions
    definitions: JSONDefinitions = consolidate_definitions(*schema, pop=True)

    return {
        ONE_OF_KEYWORD: schema,
        DEFINITIONS_KEYWORD: definitions
    }


def any_of(*schema: JSONSchema) -> JSONSchema:
    """
    Creates a schema which makes sure the value matches at least one of the
    given schema.

    :param schema:  The individual schema.
    :return:        The combined schema.
    """
    # Must provide at least 2 schema
    if len(schema) < 2:
        raise JSONSchemaError("Can't use one_of with fewer than 2 sub-schema")

    # Copy the schema into a list
    schema = deep_copy(list(schema))

    # Extract any definitions
    definitions: JSONDefinitions = consolidate_definitions(*schema, pop=True)

    return {
        ANY_OF_KEYWORD: schema,
        DEFINITIONS_KEYWORD: definitions
    }
