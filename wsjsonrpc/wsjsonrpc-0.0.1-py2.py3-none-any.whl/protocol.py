#!/usr/bin/env python
"""Protocols to add the JSON-RPC 2.0 API to WebSocket."""

import json
import re
import time
from contextlib import contextmanager

from autobahn.twisted import websocket
from twisted import logger
from twisted.internet import defer

from . import exception


class RequestBatcher(object):
    """Context manager object for creating batches of request/notify commands."""

    def __init__(self, parent):
        """
        Construct a RequestBatcher instance.

        Args:
            parent (protocol): The protcol that is creating this instance.

        """
        self.parent = parent
        self.requests = []
        self.deferreds = []

    def request(self, method, params=None, timeout=10):
        """
        Add a 'notify' request to the batch.

        Args:
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.
            timeout (int): Trigger the errback for this request after 'timeout' seconds.

        Returns:
            Deferred: A deferred that will trigger with the result of the request.

        """
        payload, df = self.parent.build_request(method, params=params, timeout=timeout)
        self.requests.append(payload)
        self.deferreds.append(df)
        return df

    def notify(self, method, params=None):
        """
        Add a 'notify' request to the batch.

        Args:
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.

        Returns:
            None

        """
        notification = self.parent.build_notification(method, params=params)
        self.requests.append(notification)
        return None

    def deferredList(self, fireOnOneCallback=0, fireOnOneErrback=0, consumeErrors=0):
        """
        Return a deferredList over the deferreds we have created for this batch.

        Args:
            fireOnOneCallback (bool): True if one callback will trigger the callback
            fireOnOneErrback (bool): True if one errback will trigger the errback
            consumeErrors (bool): True if this DeferredList should consume child errors

        Returns:
            Deferred: A deferred that fires when all deferreds complete.

        """
        return defer.DeferredList(
            self.deferreds,
            fireOnOneCallback=fireOnOneCallback,
            fireOnOneErrback=fireOnOneErrback,
            consumeErrors=consumeErrors,
        )

    def sendBatch(self):
        """Send any batched requests to the peer."""
        if not self.requests:
            return
        self.parent.sendObject(self.requests)

    def cancel(self):
        """Cancel so that you can exit the context without submitting any requests."""
        self.requests = []
        self.deferreds = []


class JsonRpcProtocolMixin(object):
    """Mixin class to add the JSON-RPC protocol to WebSocket protocol instances."""

    request_id_regex = re.compile(r'"id"\s*:\s*(\d+)')
    logger = logger.Logger()

    def __init__(self, *args, **kwargs):
        """
        Construct a JsonRpcProtocolMixin instance.

        Args:
            *args (list): An args list to pass through to our superclass
            **kwargs (dict): A kwargs dict to pass through to our superclass

        """
        super(JsonRpcProtocolMixin, self).__init__(*args, **kwargs)
        self.next_request_id = 0
        self.deferreds = {}

    def unpack(self, jsondata):
        """
        JSON-decode jsondata. As a fallback try to get at least an "id" from jsondata.

        Args:
            jsondata (str): A JSON-serialized request, response or error object.

        Raises:
            JsonRpcParseError: If the jsondata fails to deserialize.

        Returns:
            dict: A request, response or error object.

        """
        try:
            return json.loads(jsondata)
        except Exception:
            pass

        """
        Because json unpack failed, we don't know the request ID to add to our
        error message. This regex tries to salvage an ID from the broken javscript,
        and succeeds only if it finds exactly one match.
        """
        matches = self.request_id_regex.findall(jsondata)
        if len(matches) == 1:
            request_id = int(matches[0])
            raise exception.JsonRpcParseError(request_id)

        raise exception.JsonRpcParseError(None)

    def timeoutOldRequests(self):
        """
        Timeout expired requests.

        ProtocolFactory calls this method every 10 seconds to sweep expired requests.
        """
        now = time.time()
        for key in list(self.deferreds.keys()):
            df, timeout = self.deferreds[key]
            if timeout > now:
                continue
            self.deferreds.pop(key)
            try:
                df.errback(exception.JsonRpcInternalError(key))
            except Exception as e:
                self.logger.error("Failed to errback on timeout", exc=str(e))

    @contextmanager
    def batchContext(self):
        """
        Create a context and return a RequestBatcher instance.

        Within the context the user can add many requests to the RequestBatcher, and
        on leaving the context, those requests will be submitted to the peer as one
        batch.

        Yields:
            RequestBatcher: A RequestBatcher instance.

        """
        batcher = self.batch()
        try:
            yield batcher
        finally:
            """Exiting the context submits the batched requests/notifications."""
            batcher.sendBatch()

    def batch(self):
        """
        Return a RequestBatcher object populated with this instance as its parent.

        Returns:
            RequestBatcher: a RequestBatcher object.

        """
        return RequestBatcher(self)

    def handleParseError(self, e):
        """
        Return an error object that describes the Exception we've encountered.

        Args:
            e (Exception): The thing that went wrong.

        Returns:
            dict: The JSON-RPC error response object.

        """
        if not isinstance(e, exception.JsonRpcException):
            self.logger.error(
                "failed to parse json: re-casting exception",
                before=str(type(e)),
                after="JsonRpcParseError",
                exc=str(e),
            )
            e = exception.JsonRpcParseError(None)

        envelope = {
            "jsonrpc": "2.0",
            "error": {"code": e.errno, "message": e.message},
            "id": e.request_id,
        }
        return self.sendObject(envelope)

    def onMessage(self, message, isBinary):
        """
        Unpack and process message.

        A message could be a request (or batch of requests) that require responses, or
        it could be a notification or result (or batch of either) that should just be
        quietly processed without returning a result.

        Args:
            message (str): A JSON-serialized message from our peer.
            isBinary (bool): A flag to tell us if the payload is binary data.

        Returns:
            Deferred: A deferred that triggers when the request has finished or None.

        """
        try:
            payload = self.unpack(message)
        except Exception as e:
            return self.handleParseError(e)

        if isinstance(payload, (list, tuple)):
            for item in payload:
                if "method" in item:
                    return self.onBatchRequest(payload)
                elif "result" in item or "error" in item:
                    return self.onBatchResponse(payload)

            """
            The payload was bad and we don't have a request ID
            """
            return self.handleParseError(exception.JsonRpcInvalidRequest(None))

        if "method" in payload:
            if "id" in payload:
                df = self.onRequest(**payload)
                df.addCallback(self.sendObject)
                return df
            else:
                return self.onNotification(**payload)

        if "result" in payload:
            return self.onResult(payload)

        if "error" in payload:
            return self.onError(payload)

        """
        If no methods matched, then we have an invalid request.
        """
        request_id = payload.get("id")
        return self.handleParseError(exception.JsonRpcInvalidRequest(request_id))

    def next_id(self):
        """
        Return the next available request_id.

        Returns:
            int: The next available request_id in a series of incrementing integers.

        """
        next_request_id = self.next_request_id
        self.next_request_id += 1
        return next_request_id

    def request(self, method, params=None, timeout=10):
        """
        Send a request to the peer.

        A request requires a response and must have an "id".

        Args:
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.
            timeout (int): Trigger the errback on the deferred after 'timeout' seconds.

        Returns:
            Deferred: A deferred that fires when the request completes.

        """
        payload, df = self.build_request(method, params=params, timeout=timeout)
        self.sendObject(payload)
        return df

    def build_request(self, method, params=None, timeout=10):
        """
        Build a request to send to the peer.

        A request requires a response and must have an "id".

        Args:
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.
            timeout (int): Trigger the errback on the deferred after 'timeout' seconds.

        Returns:
            tuple(dict, Deferred): Tuple of a request object and its deferred.

        """
        request_id = self.next_id()
        payload = {"jsonrpc": "2.0", "method": method, "id": request_id}
        if params:
            _ = self.parseArgs(params, id=request_id)
            payload["params"] = params

        df = defer.Deferred()
        self.deferreds[request_id] = (df, time.time() + timeout)
        return payload, df

    def notify(self, method, params=None):
        """
        Send a notification to the peer.

        A notification does not require a response and must not have an "id".

        Args:
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.

        """
        notification = self.build_notification(method, params=params)
        self.sendObject(notification)

    def build_notification(self, method, params=None):
        """
        Send a notification to the peer.

        A notification does not require a response and must not have an "id".

        Args:
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.

        Returns:
            object: A JSON-RPC request object (dict) with no "id" key.

        """
        payload = {"jsonrpc": "2.0", "method": method}

        if params:
            _ = self.parseArgs(params)
            payload["params"] = params

        return payload

    def sendObject(self, value):
        """
        JSON-encode 'value' and send the result to our peer.

        Args:
            value (object): Any JSON-serializable value.

        """
        if value is None:
            return
        self.sendMessage(json.dumps(value).encode("utf-8"))

    def parseArgs(self, params, id=None):
        """
        Parse the arguments for an API method.

        Args:
            params (object): A list or dict of arguments for the API method.
            id (int): The request ID - always None in this method.

        Raises:
            JsonRpcInvalidParams: The params were incorrectly formatted.

        Returns:
            tuple(list, dict): Arguments for the API method.

        """
        args = []
        kwargs = {}

        if isinstance(params, (list, tuple)):
            args = params
        elif isinstance(params, dict):
            kwargs = params
        elif params is not None:
            self.logger.error(
                "wrong datatype for 'params' - expected "
                "dict|list|tuple|None got '{}'".format(type(params))
            )
            raise exception.JsonRpcInvalidParams(id)

        return args, kwargs

    def parseRequest(self, method, params, id=None):
        """
        Process a request, and return a callable and its arguments.

        Args:
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.
            id (int): The request ID - always None in this method.

        Raises:
            JsonRpcMethodNotFound: No callable could be found for the requested name.

        Returns:
            tuple(callable, list, dict): A callable and its arguments

        """
        _method = self.factory.registry.get(method)

        if not _method:
            raise exception.JsonRpcMethodNotFound(id)
        args, kwargs = self.parseArgs(params, id=id)
        return _method, args, kwargs

    def onNotification(self, jsonrpc=None, method=None, params=None, id=None):
        """
        Process a notification, and do not return a result.

        Args:
            jsonrpc (None): The jsonrpc keyword occurs in all request objects.
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.
            id (int): The request ID - always None in this method.

        """
        try:
            _method, args, kwargs = self.parseRequest(method, params, id)
        except exception.JsonRpcException as e:
            self.logger.error("method call failed: {}".format(e), e=str(e))
            return
        except Exception as e:
            self.logger.error("method call failed: {}".format(e), e=str(e))
            return

        try:
            self.factory.runMethod(_method, self, *args, **kwargs)
        except Exception as e:
            self.logger.error(
                "request method execution failed",
                e=str(e),
                method=method,
                params=params,
            )

    def onBatchRequest(self, batch):
        """
        Respond to a list of requests, returning a list of results.

        This method attaches a deferred to the list of requests. When all the requests
        have completed, the deferred is called with a list of their results.

        Args:
            batch (list): List of JSON-RPC 2.0 request objects.

        Returns:
            list: A list of results wrapped in a deferred.

        """
        results = []
        for request in batch:
            if "id" in request:
                results.append(self.onRequest(**request))
            else:
                self.onNotification(**request)
                continue

        df = defer.gatherResults(results)
        df.addCallback(self.sendObject)
        return df

    def onRequest(self, jsonrpc=None, method=None, params=None, id=None):
        """
        Return a deferred whose result is a response object from an API method.

        Args:
            jsonrpc (None): The jsonrpc keyword occurs in all request objects.
            method (str): A string that identifies an API method to remote peers.
            params (object): A list or dict of arguments for the API method.
            id (int): The request ID (or None for a notification).

        Returns:
            Deferred: A deferred which will trigger with the API method's result.

        """
        try:
            _method, args, kwargs = self.parseRequest(method, params, id)
        except exception.JsonRpcException as e:
            # Although we're in an error state, it is proper to call defer.succeed here.
            return defer.succeed(self.packageExceptionObject(e, id))

        try:
            df = defer.maybeDeferred(
                self.factory.runMethod, _method, self, *args, **kwargs
            )
        except Exception as e:
            self.logger.error(
                "nofity method execution failed: {}".format(e),
                e=str(e),
                method=method,
                params=params,
            )
            df = defer.fail(exception.JsonRpcInternalError(id))

        df.addCallback(self.packageResult, id)
        df.addErrback(self.packageFailureObject, id)
        return df

    def onBatchResponse(self, batch):
        """
        Process a batch of response objects.

        Args:
            batch (list): List of JSON-RPC response (or error) objects.

        """
        for response in batch:
            self.logger.debug("onReponse")
            if "result" in response:
                self.onResult(response)
            elif "error" in response:
                self.onError(response)

    def onError(self, payload):
        """
        Process an incoming error payload - a remote API call failed.

        Procesing the result of a remote API method call means finding any deferreds
        that were waiting for that result value and calling their errback with an
        exception based on the result value.

        Args:
            payload (dict): A result object from a remote API method that we called.

        Returns:
            Deferred: A deferred that has been errored with the result from the payload.

        """
        self.logger.error("onError")
        result = payload["error"]
        request_id = payload["id"]
        df, timeout = self.deferreds.pop(request_id)
        exc = exception.JsonRpcExceptionFactory.create_exception(request_id, **result)
        df.errback(exc)
        return df

    def onResult(self, payload):
        """
        Process an incoming result payload.

        Procesing the result of a remote API method call means finding any deferreds
        that were waiting for that result value and calling them with the value.

        Args:
            payload (dict): A result object from a remote API method that we called.

        Returns:
            Deferred: A deferred that has been called with the result from the payload.

        """
        result = payload["result"]
        request_id = payload.get("id")
        if request_id is None:
            self.logger.error(
                "bad response from client - missing 'id'", payload=payload
            )
            return
        df, timeout = self.deferreds.pop(request_id)
        df.callback(result)
        return df

    def packageResult(self, result, request_id):
        """
        Return a JSON-RPC result object (ready for JSON serialization).

        Args:
            result (object): Result of API method.
            request_id (int): The request_id associated with the method.

        Returns:
            dict: A well-formed JSON-RPC result object (ready for JSON serialization).

        """
        envelope = {"jsonrpc": "2.0", "result": result, "id": request_id}
        return envelope

    def packageFailureObject(self, failure, request_id):
        """
        Return a JSON-RPC error object (ready for JSON serialization).

        Args:
            failure (twisted.python.failure.Failure): Failure representing the failure.
            request_id (int): The request_id associated with the method that failed.

        Returns:
            dict: A well-formed JSON-RPC error object (ready for JSON serialization).

        """
        return self.packageExceptionObject(failure.value, request_id)

    def packageExceptionObject(self, _exception, request_id):
        """
        Return a JSON-RPC error object (ready for JSON serialization).

        Args:
            _exception (Exception): JsonRpcException representing the failure.
            request_id (int): The request_id associated with the method that failed.

        Returns:
            dict: A well-formed JSON-RPC error object (ready for JSON serialization).

        """
        try:
            code, message, request_id = (
                _exception.errno,
                _exception.message,
                _exception.request_id,
            )
        except Exception as e:
            self.logger.error("failed to get exception args", e=e)
            code, message = exception.JsonRpcException.internal_error

        if request_id is None:
            return

        envelope = {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": request_id,
        }
        return envelope


class JsonRpcClientProtocol(JsonRpcProtocolMixin, websocket.WebSocketClientProtocol):
    """Client protocol for the JSON-RPC 2.0 API standard."""

    def onOpen(self):
        """
        Notify the client factory that a protocol (self) is ready.

        This instance will be added to the factory's DeferredQueue for protocols, so
        that client code can get a reference to it.
        """
        self.factory.protocolReady(self)


class JsonRpcServerProtocol(JsonRpcProtocolMixin, websocket.WebSocketServerProtocol):
    """Server protocol for the JSON-RPC 2.0 API standard."""
