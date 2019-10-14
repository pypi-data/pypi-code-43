# coding=utf-8
# Licensed Materials - Property of IBM
# Copyright IBM Corp. 2019

import datetime
from tempfile import gettempdir
import streamsx.spl.op
import streamsx.spl.types
from streamsx.topology.schema import CommonSchema, StreamSchema
from streamsx.spl.types import rstring
import streamsx.spl.toolkit as tk
from streamsx.toolkits import download_toolkit

_TOOLKIT_NAME = 'com.ibm.streamsx.inetserver'

def _add_toolkit_dependency(topo, version):
    # IMPORTANT: Dependency of this python wrapper to a specific toolkit version
    # This is important when toolkit is not set with streamsx.spl.toolkit.add_toolkit (selecting toolkit from remote build service)
    tk.add_toolkit_dependency(topo, _TOOLKIT_NAME, version)


def download_toolkit(url=None, target_dir=None):
    r"""Downloads the latest Inetserver toolkit from GitHub.

    Example for updating the Inetserver toolkit for your topology with the latest toolkit from GitHub::

        import streamsx.endpoint as endpoint
        import streamsx.spl.toolkit as tk
        # download toolkit from GitHub
        toolkit_location = endpoint.download_toolkit()
        # add the toolkit to topology
        tk.add_toolkit(topology, toolkit_location)

    Example for updating the topology with a specific version of the toolkit using a URL::

        import streamsx.endpoint as endpoint
        import streamsx.spl.toolkit as tk
        url430 = 'https://github.com/IBMStreams/streamsx.inetserver/releases/download/v4.3.0/streamsx.inetserver-4.3.0-104fb9b-20191011-1712.tgz'
        toolkit_location = endpoint.download_toolkit(url=url430)
        tk.add_toolkit(topology, toolkit_location)

    Args:
        url(str): Link to toolkit archive (\*.tgz) to be downloaded. Use this parameter to 
            download a specific version of the toolkit.
        target_dir(str): the directory where the toolkit is unpacked to. If a relative path is given,
            the path is appended to the system temporary directory, for example to /tmp on Unix/Linux systems.
            If target_dir is ``None`` a location relative to the system temporary directory is chosen.

    Returns:
        str: the location of the downloaded toolkit

    .. note:: This function requires an outgoing Internet connection
    """
    _toolkit_location = streamsx.toolkits.download_toolkit (toolkit_name=_TOOLKIT_NAME, url=url, target_dir=target_dir)
    return _toolkit_location


def inject(topology, name, monitor, context=None, schema=CommonSchema.Json):
    """Receives HTTP POST requests.

    Embeds a Jetty web server to allow HTTP/HTTPS POST requests with the following mime types to be submitted as tuple on the output stream:

    .. csv-table::
        :header: schema, content-type

        CommonSchema.Json, application/json
        CommonSchema.XML, application/xml
        CommonSchema.String, application/x-www-form-urlencoded
        StreamSchema, application/x-www-form-urlencoded

    Example for JSON injection::

        import streamsx.endpoint as endpoint
        topo = Topology()
        s1 = endpoint.inject(topo, name='jsoninject', context='sample')
        s1.print()

    Args:
        topology: The Streams topology.
        name(str): Source name in the Streams context. This name is part of the URL.
        monitor(str): The name of the endpoint-monitor that provides the ssl configuration for this endpoint. If it is None, the connection uses plain HTTP
        context(str): Defines an URL context path. URL contains ``context``/``name``.
        schema: Schema for returned Stream, default is ``CommonSchema.Json``

    Returns:
        Output Stream with schema defined in ``schema`` parameter (default ``CommonSchema.Json``).
    """

    _add_toolkit_dependency(topology, '4.3.0')

    if schema is CommonSchema.Json:
        kind = 'com.ibm.streamsx.inet.rest::HTTPJSONInjection'
    elif schema is CommonSchema.XML:
        kind = 'com.ibm.streamsx.inet.rest::HTTPXMLInjection'
    elif (schema is CommonSchema.String) or (isinstance(schema, StreamSchema)):
        kind = 'com.ibm.streamsx.inet.rest::HTTPTupleInjection'
    else:
        raise ValueError(schema)

    sslAppConfigName = None
    if monitor is not None:
        sslAppConfigName = monitor + '-streams-certs'

    _op = _HTTPInjection(topology, kind=kind, context=context, schema=schema, name=name, sslAppConfigName=sslAppConfigName)
    return _op.outputs[0]


def expose(window, name, monitor, context=None):
    """REST HTTP/HTTPS API to view tuples from windowed input ports.

    Embeds a Jetty web server to provide HTTP REST access to the collection of tuples in the input port window at the time of the last eviction for tumbling windows, or last trigger for sliding windows.

    Example with a sliding window::

        import streamsx.endpoint as endpoint
        s = topo.source([{'a': 'Hello'}, {'a': 'World'}, {'a': '!'}]).as_json()
        endpoint.expose(window=s.last(3).trigger(1), name='tupleview', context='sample')

    The URL containing "**context**/**name**" for the sample above ends with: ``/sample/tupleview/ports/input/0/tuples``

    Args:
        window(Window): Windowed stream of tuples that will be viewable using a HTTP GET request. 
        name(str): Sink name in the Streams context. This name is part of the URL.
        monitor(str): The name of the endpoint-monitor that provides the ssl configuration for this endpoint. If it is None, the connection uses plain HTTP
        context(str): Defines an URL context path. URL contains ``context``/``name``.

    Returns:
        streamsx.topology.topology.Sink: Stream termination.
    """

    _add_toolkit_dependency(window.topology, '4.3.0')

    sslAppConfigName = None
    if monitor is not None:
        sslAppConfigName = monitor + '-streams-certs'

    _op = _HTTPTupleView(window, context=context, name=name, sslAppConfigName=sslAppConfigName)
    return streamsx.topology.topology.Sink(_op)



class _HTTPInjection(streamsx.spl.op.Source):

    def __init__(self, topology, kind, schema=None, certificateAlias=None, context=None, contextResourceBase=None, keyPassword=None, keyStore=None, keyStorePassword=None, port=0, trustStore=None, trustStorePassword=None, sslAppConfigName=None, vmArg=None, name=None):
        topology = topology
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if certificateAlias is not None:
            params['certificateAlias'] = certificateAlias 
        if context is not None:
            params['context'] = context
        if contextResourceBase is not None:
            params['contextResourceBase'] = contextResourceBase
        if keyPassword is not None:
            params['keyPassword'] = keyPassword
        if keyStore is not None:
            params['keyStore'] = keyStore
        if keyStorePassword is not None:
            params['keyStorePassword'] = keyStorePassword
        if port is not None:
            params['port'] = port
        if trustStore is not None:
            params['trustStore'] = trustStore
        if trustStorePassword is not None:
            params['trustStorePassword'] = trustStorePassword
        if sslAppConfigName is not None:
            params['sslAppConfigName'] = sslAppConfigName

        super(_HTTPInjection, self).__init__(topology,kind,schema,params,name)


class _HTTPTupleView(streamsx.spl.op.Sink):

    def __init__(self, stream, certificateAlias=None, context=None, contextResourceBase=None, forceEmpty=None, headers=None, host=None, keyPassword=None, keyStore=None, keyStorePassword=None, namedPartitionQuery=None, partitionBy=None, partitionKey=None, port=0, trustStore=None, trustStorePassword=None, sslAppConfigName=None, vmArg=None, name=None):
        topology = stream.topology
        kind="com.ibm.streamsx.inet.rest::HTTPTupleView"
        params = dict()
        if vmArg is not None:
            params['vmArg'] = vmArg
        if certificateAlias is not None:
            params['certificateAlias'] = certificateAlias
        if context is not None:
            params['context'] = context
        if contextResourceBase is not None:
            params['contextResourceBase'] = contextResourceBase
        if forceEmpty is not None:
            params['forceEmpty'] = forceEmpty
        if headers is not None:
            params['headers'] = headers
        if host is not None:
            params['host'] = host
        if keyPassword is not None:
            params['keyPassword'] = keyPassword
        if keyStore is not None:
            params['keyStore'] = keyStore
        if keyStorePassword is not None:
            params['keyStorePassword'] = keyStorePassword
        if namedPartitionQuery is not None:
            params['namedPartitionQuery'] = namedPartitionQuery
        if partitionBy is not None:
            params['partitionBy'] = partitionBy
        if partitionKey is not None:
            params['partitionKey'] = partitionKey
        if port is not None:
            params['port'] = port
        if trustStore is not None:
            params['trustStore'] = trustStore
        if trustStorePassword is not None:
            params['trustStorePassword'] = trustStorePassword
        if sslAppConfigName is not None:
            params['sslAppConfigName'] = sslAppConfigName

        super(_HTTPTupleView, self).__init__(kind,stream,params,name)

