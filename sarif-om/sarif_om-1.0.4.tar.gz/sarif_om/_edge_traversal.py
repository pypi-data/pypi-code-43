# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class EdgeTraversal(object):
    """Represents the traversal of a single edge during a graph traversal."""

    edge_id = attr.ib(metadata={"schema_property_name": "edgeId"})
    final_state = attr.ib(default=None, metadata={"schema_property_name": "finalState"})
    message = attr.ib(default=None, metadata={"schema_property_name": "message"})
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
    step_over_edge_count = attr.ib(default=None, metadata={"schema_property_name": "stepOverEdgeCount"})
