"""
Module for constants related to JSON validation schema.
"""
# Keywords
ADDITIONAL_PROPERTIES_KEYWORD: str = "additionalProperties"  # The schema for validating any additional properties
ANY_OF_KEYWORD: str = "anyOf"  # For matching against any one of a number of schema
CONSTANT_KEYWORD: str = "const"  # For validating against a constant value
DEFINITIONS_KEYWORD: str = "definitions"  # For defining reference schema
ENUMERATION_KEYWORD: str = "enum"  # For validating against a set of constant values
EXCLUSIVE_MAXIMUM_KEYWORD: str = "exclusiveMaximum"  # The exclusive maximum of a numeric type
EXCLUSIVE_MINIMUM_KEYWORD: str = "exclusiveMinimum"  # The exclusive minimum of a numeric type
FORMAT_KEYWORD: str = "format"  # The custom format to match strings against
ITEMS_KEYWORD: str = "items"  # The schema to validate elements of an array
MAXIMUM_KEYWORD: str = "maximum"  # The maximum value of a numeric type
MAX_ITEMS_KEYWORD: str = "maxItems"  # The maximum number of items in an array
MAX_LENGTH_KEYWORD: str = "maxLength"  # The maximum length of a string
MINIMUM_KEYWORD: str = "minimum"  # The minimum value of a numeric type
MIN_ITEMS_KEYWORD: str = "minItems"  # The minimum number of items in an array
MIN_LENGTH_KEYWORD: str = "minLength"  # The minimum length of a string
MULTIPLE_OF_KEYWORD: str = "multipleOf"  # The divisor of numeric types
ONE_OF_KEYWORD: str = "oneOf"  # For validating against exactly one of a number of schema
PATTERN_KEYWORD: str = "pattern"  # The regex pattern to match against strings
PROPERTIES_KEYWORD: str = "properties"  # The schema for validating object properties
REFERENCE_KEYWORD: str = "$ref"  # For referring to reference schema
REQUIRED_PROPERTIES_KEYWORD: str = "required"  # The names of required object properties
TYPE_KEYWORD: str = "type"  # The type of JSON element to validate
UNIQUE_ITEMS_KEYWORD: str = "uniqueItems"  # Whether all elements in an array must be unique

# Types
ARRAY_TYPE: str = "array"
INTEGER_TYPE: str = "integer"
NUMBER_TYPE: str = "number"
OBJECT_TYPE: str = "object"
STRING_TYPE: str = "string"
BOOL_TYPE: str = "boolean"
NULL_TYPE: str = "null"
