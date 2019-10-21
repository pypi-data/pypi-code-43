"""
Module for reusable JSON schema definitions and references to them.
Also provides tools for relative JSON pointer syntax.
"""
from .constants import *
from ._static import NULL_SCHEMA, BOOL_SCHEMA, FLOAT_SCHEMA, STRING_SCHEMA
from ._typing import JSONSchema, JSONDefinitions


def reference_string(referend: str) -> str:
    """
    Creates a JSON pointer reference string to the given referend.

    :param referend:    The referend.
    :return:            The reference string.
    """
    return f"#/{DEFINITIONS_KEYWORD}/{referend}"


def reference_schema(referend: str) -> JSONSchema:
    """
    Returns a reference schema to the given referend.

    :param referend:    The referend.
    :return:            The schema.
    """
    return {REFERENCE_KEYWORD: reference_string(referend)}


def extract_definitions(schema: JSONSchema, pop: bool = False) -> JSONDefinitions:
    """
    Extracts the definitions for the given JSON schema.

    :param schema:  The schema.
    :param pop:     Whether to pop the definitions or leave them in place.
    :return:        The definitions.
    """
    # Trivial schema have no definitions
    if isinstance(schema, bool):
        return {}

    # If there are no definitions, return an empty set
    if DEFINITIONS_KEYWORD not in schema:
        return {}

    # Get or pop the definitions as requested
    if pop:
        return schema.pop(DEFINITIONS_KEYWORD)
    else:
        return schema.get(DEFINITIONS_KEYWORD)


def consolidate_definitions(*schemata: JSONSchema, pop: bool = False) -> JSONDefinitions:
    """
    Consolidates the definitions from a number of schemata,
    checking for collisions.

    :param schemata:        The schemas to collect definitions from.
    :param pop:             Whether to pop the definitions or leave them in place.
    :return:                The definitions.
    """
    # Create the results set
    consolidated_definitions = {}

    # Process each schema in turn
    for schema in schemata:
        extracted_definitions = extract_definitions(schema, pop)
        for definition_name, definition in extracted_definitions.items():
            if definition_name in consolidated_definitions and consolidated_definitions[definition_name] != definition:
                raise ValueError(f"Error composing definitions: definition '{definition_name}' "
                                 f"defined more than once")
            consolidated_definitions[definition_name] = definition

    return consolidated_definitions


# Definition of a schema which validates any JSON
IS_JSON_REFERENCE: str = "is-json"
IS_JSON_REFEREND: str = reference_string(IS_JSON_REFERENCE)
IS_JSON_SCHEMA: JSONSchema = reference_schema(IS_JSON_REFERENCE)
IS_JSON_DEFINITION: JSONDefinitions = {
    IS_JSON_REFERENCE: {
        ANY_OF_KEYWORD: [
            NULL_SCHEMA,
            BOOL_SCHEMA,
            FLOAT_SCHEMA,
            STRING_SCHEMA,
            {TYPE_KEYWORD: OBJECT_TYPE, ADDITIONAL_PROPERTIES_KEYWORD: IS_JSON_SCHEMA},
            {TYPE_KEYWORD: ARRAY_TYPE, ITEMS_KEYWORD: IS_JSON_SCHEMA}
        ]
    }
}