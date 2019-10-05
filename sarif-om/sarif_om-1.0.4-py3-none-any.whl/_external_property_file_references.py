# This file was generated by jschema_to_python version 1.2.3.

import attr


@attr.s
class ExternalPropertyFileReferences(object):
    """References to external property files that should be inlined with the content of a root log file."""

    addresses = attr.ib(default=None, metadata={"schema_property_name": "addresses"})
    artifacts = attr.ib(default=None, metadata={"schema_property_name": "artifacts"})
    conversion = attr.ib(default=None, metadata={"schema_property_name": "conversion"})
    driver = attr.ib(default=None, metadata={"schema_property_name": "driver"})
    extensions = attr.ib(default=None, metadata={"schema_property_name": "extensions"})
    externalized_properties = attr.ib(default=None, metadata={"schema_property_name": "externalizedProperties"})
    graphs = attr.ib(default=None, metadata={"schema_property_name": "graphs"})
    invocations = attr.ib(default=None, metadata={"schema_property_name": "invocations"})
    logical_locations = attr.ib(default=None, metadata={"schema_property_name": "logicalLocations"})
    policies = attr.ib(default=None, metadata={"schema_property_name": "policies"})
    properties = attr.ib(default=None, metadata={"schema_property_name": "properties"})
    results = attr.ib(default=None, metadata={"schema_property_name": "results"})
    taxonomies = attr.ib(default=None, metadata={"schema_property_name": "taxonomies"})
    thread_flow_locations = attr.ib(default=None, metadata={"schema_property_name": "threadFlowLocations"})
    translations = attr.ib(default=None, metadata={"schema_property_name": "translations"})
    web_requests = attr.ib(default=None, metadata={"schema_property_name": "webRequests"})
    web_responses = attr.ib(default=None, metadata={"schema_property_name": "webResponses"})
