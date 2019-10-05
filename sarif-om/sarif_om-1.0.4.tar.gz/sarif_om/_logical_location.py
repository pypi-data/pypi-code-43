# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class LogicalLocation(object):
    """A logical location of a construct that produced a result."""

    decorated_name = attr.ib(default=None, metadata={"schema_property_name": "decoratedName"})
    fully_qualified_name = attr.ib(default=None, metadata={"schema_property_name": "fullyQualifiedName"})
    index = attr.ib(default=-1, metadata={"schema_property_name": "index"})
    kind = attr.ib(default=None, metadata={"schema_property_name": "kind"})
    name = attr.ib(default=None, metadata={"schema_property_name": "name"})
    parent_index = attr.ib(default=-1, metadata={"schema_property_name": "parentIndex"})
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
