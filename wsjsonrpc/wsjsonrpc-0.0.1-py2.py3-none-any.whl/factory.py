#!/usr/bin/env python
"""Protocol Factories for wsjsonrpc : JSON-RPC 2.0 over WebSockets."""

from autobahn.twisted import websocket
from twisted import logger
from twisted.internet import defer, reactor, task

from .protocol import JsonRpcClientProtocol, JsonRpcServerProtocol


class JsonRpcWebSocketFactoryMixin(object):
    """
    Mix this with a client or server protocol factory.

    See the implementations below for a suggestion on how to proceed.
    """

    logger = logger.Logger()
    sem = None

    def __init__(self, *args, **kwargs):
        """
        Construct a JsonRpcWebSocketFactoryMixin instance.

        This class won't do much on its own - it needs to be mixed in with either a
        websocket.WebSocketClientFactory or websocket.WebSocketServerFactory class,
        as you can see in the examples below.

        Because the JSON-RPC 2.0 protocol is fully symmetric, bidirectional and
        asynchronous, this class provides the protocol implementation for both the
        server the client.

        Args:
            *args (list): An args list to pass through to the superclass.
            **kwargs (dict): A kwargs dict to pass through to the superclass.

        """
        concurrency = kwargs.pop("concurrency", None)
        super(JsonRpcWebSocketFactoryMixin, self).__init__(*args, **kwargs)

        if concurrency is not None:
            try:
                concurrency = int(concurrency)
            except Exception as e:
                self.logger.error(
                    "failed to cast concurrency value to int",
                    e=str(e),
                    concurrency=concurrency,
                )
                concurrency = None
            else:
                if concurrency < 1:
                    concurrency = None

        if concurrency:
            self.__class__.sem = defer.DeferredSemaphore(concurrency)

        self._protocols = set()
        self.timeout_loop = None
        self.beginLooping()
        self.registry = {}

    def runMethod(self, method, protocol, *args, **kwargs):
        """
        Return the results of a remote method call to our peer.

        Args:
            method (str): A string that identifies an API method to remote peers.
            protocol (JsonRpcProtocolMixin): A JsonRpcProtocol instance.
            *args (list): Args to pass through to the API method.
            **kwargs (dict): Kwargs to pass through to the API method.

        Returns:
            object: The return value of the API method, whatever that might be.

        """
        if self.sem is None:
            return method(protocol, *args, **kwargs)
        return self.sem.run(method, protocol, *args, **kwargs)

    def connectionLost(self, connection):
        """
        De-register a closed protocol from our _protocols attribute.

        Args:
            connection (JsonRpcProtocolMixin): A protocol that has just disconnected.

        """
        try:
            self._protocols.remove(connection)
        except Exception:
            self.logger.error("Tried to remove connection from wrong factory.")

    def buildProtocol(self, addr):
        """
        Register a newly-created protocol in our _protocols attribute, and return it.

        Args:
            addr (asdf): Normally an IPv4Address or IPv6Address.

        Returns:
            JsonRpcServerProtocol: The freshly-connected protocol instance.

        """
        protocol = super(JsonRpcWebSocketFactoryMixin, self).buildProtocol(addr)
        self._protocols.add(protocol)
        return protocol

    def beginLooping(self):
        """
        Start the timeout_loop on this instance if it's not already running.

        The timeout loop periodically scavenges for requests with expired timeouts.
        """
        if self.timeout_loop is not None:
            return

        self.timeout_loop = task.LoopingCall(self.timeoutOldRequests)
        self.timeout_loop.start(10, False)

    def timeoutOldRequests(self):
        """
        Call the errback method on any protocol whose timeout has expired.

        Iterate over each protocol we created and call its timeoutOldRequests method.
        """
        for protocol in self._protocols:
            protocol.timeoutOldRequests()

    def registerMethod(self, name, method):
        """
        Register a method name and a method as available for remote execution.

        The first argument to the method MUST be the protocol instance for the client.
        See the runMethod method on this class for details.

        Args:
            name (str): The name that remote peers will call for this method.
            method (callable): The actual method that will get called.

        Raises:
            Exception: Can't re-register a remote method name

        """
        if name in self.registry:
            raise Exception(
                "method name '{}' is already represented in "
                "AssemblyWebSocketServerFactory.registry by '{}'".format(
                    name, self.registry[name]
                )
            )
        self.registry[name] = method


class JsonRpcWebSocketServerFactory(
    JsonRpcWebSocketFactoryMixin, websocket.WebSocketServerFactory
):
    """Factory for JsonRpcServerProtocol objects."""

    protocol = JsonRpcServerProtocol


class JsonRpcWebSocketClientFactory(
    JsonRpcWebSocketFactoryMixin, websocket.WebSocketClientFactory
):
    """Factory for JsonRpcClientProtocol objects."""

    protocol = JsonRpcClientProtocol

    def __init__(self, *args, **kwargs):
        """
        Construct a JsonRpcWebSocketClientFactory instance.

        Args:
            *args (list): An args list to pass through to our superclass
            **kwargs (dict): A kwargs dict to pass through to our superclass

        """
        super(JsonRpcWebSocketClientFactory, self).__init__(*args, **kwargs)
        self._client_queue = defer.DeferredQueue()

    def getProtocol(self):
        """
        Return a deferred that fires with a connected protocol when it is ready.

        Returns:
            JsonRpcClientProtocol: A new connected protocol instance.

        """
        return self._client_queue.get()

    def protocolReady(self, protocol):
        """
        Put a freshly-created protocol instance on our async queue.

        Client code that's waiting for a protocol instance is given a deferred that
        belongs to this _client_queue DeferredQueue. When we put this freshly-created
        protocol on the queue, that deferred will succeed and the client code can
        proceed with it.

        Args:
            protocol (JsonRpcClientProtocol): A new connected protocol instance.

        """
        self._client_queue.put(protocol)


def get_client(protocol=u"ws", hostname=u"localhost", port=8095, path=u"jsonrpcws"):
    """
    Connect to a server and return a connected instance of JsonRpcClientProtocol.

    Args:
        protocol (str): The connection protcol - either 'ws' or (for TLS) 'wss'
        hostname (str): The hostname of the server
        port (int): The listening port on the server
        path (str): The route to the websocket service on the server, e.g. /home/jim

    Returns:
        JsonRpcClientProtocol: A connected client protocol.

    """
    if (protocol, port) in ((u"ws", 80), (u"wss", 443)):
        url = u"{}://{}:{}/{}".format(protocol, hostname, path.lstrip(u"/"))
    else:
        url = u"{}://{}:{}/{}".format(protocol, hostname, port, path.lstrip(u"/"))

    factory = JsonRpcWebSocketClientFactory(url)
    if protocol == u"ws":
        reactor.connectTCP(hostname, port, factory)
    elif protocol == u"wss":
        reactor.connectSSL(hostname, port, factory)

    return factory.getProtocol()
