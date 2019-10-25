"""
    gRPC call interceptors.
    Used to modify metadata on each RPC.
    Can be useful for adding 'authorization' headers containing bearer tokens.

    Based on original gRPC example code.
"""
import grpc
import collections

class _ClientCallDetails(collections.namedtuple('_ClientCallDetails',
                            ('method', 'timeout', 'metadata', 'credentials')),
                         grpc.ClientCallDetails):
        """Wrapper class to provide access to internal grcp.ClientCallDetails."""
        pass

class ClientCallInterceptor(grpc.UnaryUnaryClientInterceptor,
                            grpc.UnaryStreamClientInterceptor,
                            grpc.StreamUnaryClientInterceptor,
                            grpc.StreamStreamClientInterceptor):
    """
    Interceptor for any RPC type which manipulates each client call details.
    Invoked with a function to manipulate the client call details on each call.
    """

    def __init__(self, client_call_details_manipulator):
        """Pass a function that takes grpc client call details as argument.
        The function returns the modified client call details.
        """
        self._fn = client_call_details_manipulator

    def intercept_unary_unary(self, continuation, client_call_details, request):
        new_details = self._fn(client_call_details)

        return continuation(new_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        new_details = self._fn(client_call_details)
        return continuation(new_details, request)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        new_details = self._fn(client_call_details)
        return continuation(new_details, request_iterator)

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        new_details = self._fn(client_call_details)
        return continuation(new_details, request_iterator)

def header_adder_interceptor(header, value):
    """Return a ClientCallInterceptor that adds '<@header>: <@value> to each RPC call.
    """
    def intercept_call(client_call_details):
        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        metadata.append( (header, value) )

        return _ClientCallDetails(client_call_details.method,
                                  client_call_details.timeout,
                                  metadata,
                                  client_call_details.credentials)

    return ClientCallInterceptor(intercept_call)

def access_token_auth(access_token):
    """Returns a ClientCallInterceptor which authenticates each call with @access_token."""
    return header_adder_interceptor('authorization', 'Bearer {}'.format(access_token))
