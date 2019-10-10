#!/usr/bin/env python
"""
Custom exceptions for wsjsonrpc : JSON-RPC 2.0 over WebSockets.

When the code raises one of these exceptions, it will be captured and an error message
will be sent to the peer which conforms to the JSON-RPC specification, e.g. if your
code raises a JsonRpcInvalidRequest exception for request 1234, this JSON will be sent
to the peer:

{
    "jsonrpc": "2.0",
    "error": {
        "code": -32600,
        "message": "Invalid Request"
    },
    "id": 1234
    }
"""


class JsonRpcException(Exception):
    """Base class for wsjsonrpc custom exceptions."""

    json_parse_error = (-32700, "Parse error")
    invalid_request = (-32600, "Invalid Request")
    invalid_params = (-32602, "Invalid params")
    internal_error = (-32603, "Internal error")
    method_not_found = (-32601, "Method not found")

    def __str__(self):
        """
        Return the string representation for this exception instance.

        Returns:
            str: A string summary of the instance

        """
        return "request_id: {}  errno: {}  message: {}".format(
            self.request_id, self.errno, self.message
        )


class JsonRpcParseError(JsonRpcException):
    """Failed to parse an incoming message."""

    def __init__(self, request_id):
        """
        Create exception for request_id (or None for notifications).

        Args:
            request_id (int): The submitted request ID

        """
        self.request_id = request_id
        self.errno, self.message = self.json_parse_error


class JsonRpcInvalidRequest(JsonRpcException):
    """Incoming request was invalid."""

    def __init__(self, request_id):
        """
        Create exception for request_id (or None for notifications).

        Args:
            request_id (int): The submitted request ID

        """
        self.request_id = request_id
        self.errno, self.message = self.invalid_request


class JsonRpcInvalidParams(JsonRpcException):
    """Incoming request had invalid parameters (must be dict or list)."""

    def __init__(self, request_id):
        """
        Create exception for request_id (or None for notifications).

        Args:
            request_id (int): The submitted request ID

        """
        self.request_id = request_id
        self.errno, self.message = self.invalid_params


class JsonRpcInternalError(JsonRpcException):
    """An error occurred while processing an incoming request."""

    def __init__(self, request_id):
        """
        Create exception for request_id (or None for notifications).

        Args:
            request_id (int): The submitted request ID

        """
        self.request_id = request_id
        self.errno, self.message = self.internal_error


class JsonRpcMethodNotFound(JsonRpcException):
    """An incoming request tried to execute a non-existent method."""

    def __init__(self, request_id):
        """
        Create exception for request_id (or None for notifications).

        Args:
            request_id (int): The submitted request ID

        """
        self.request_id = request_id
        self.errno, self.message = self.method_not_found


class JsonRpcCustomException(JsonRpcException):
    """Subclass this to create custom application-specific exceptions."""

    def __init__(self, request_id, code, message):
        """
        Create exception for request_id (or None for notifications).

        Args:
            request_id (int): The submitted request ID
            code (int): The JSON-RPC 2.0 error code
            message (str): The JSON-RPC 2.0 error message

        """
        self.request_id = request_id
        self.errno, self.message = code, message


class JsonRpcExceptionFactory(object):
    """Create the correct exception for a given error code per the JSONRPC spec."""

    exceptions = dict(
        (
            (-32700, JsonRpcParseError),
            (-32600, JsonRpcInvalidRequest),
            (-32602, JsonRpcInvalidParams),
            (-32603, JsonRpcInternalError),
            (-32601, JsonRpcMethodNotFound),
        )
    )

    @classmethod
    def create_exception(cls, request_id, code=None, message=None):
        """
        Return an exception of the correct type for the error code.

        Args:
            request_id (int): The submitted request ID
            code (int): The JSON-RPC 2.0 error code
            message (str): The JSON-RPC 2.0 error message

        Returns:
            JsonRpcException: An instance of the correct exception type.

        """
        exc = cls.exceptions.get(code)
        if exc:
            return exc(request_id)
        return JsonRpcCustomException(request_id, code, message)
