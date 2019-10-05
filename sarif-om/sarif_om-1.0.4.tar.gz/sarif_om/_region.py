# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class Region(object):
    """A region within an artifact where a result was detected."""

    byte_length = attr.ib(default=None, metadata={"schema_property_name": "byteLength"})
    byte_offset = attr.ib(default=-1, metadata={"schema_property_name": "byteOffset"})
    char_length = attr.ib(default=None, metadata={"schema_property_name": "charLength"})
    char_offset = attr.ib(default=-1, metadata={"schema_property_name": "charOffset"})
    end_column = attr.ib(default=None, metadata={"schema_property_name": "endColumn"})
    end_line = attr.ib(default=None, metadata={"schema_property_name": "endLine"})
    message = attr.ib(default=None, metadata={"schema_property_name": "message"})
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
    snippet = attr.ib(default=None, metadata={"schema_property_name": "snippet"})
    source_language = attr.ib(default=None, metadata={"schema_property_name": "sourceLanguage"})
    start_column = attr.ib(default=None, metadata={"schema_property_name": "startColumn"})
    start_line = attr.ib(default=None, metadata={"schema_property_name": "startLine"})
