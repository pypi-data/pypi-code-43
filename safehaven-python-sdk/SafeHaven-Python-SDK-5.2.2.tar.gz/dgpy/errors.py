"""
    Custom errors and error handling decorators.
"""
import grpc

__all__ = [ 'handle_exceptions',
        'LegacyMessageError', 'GrpcError', 'TimeOutError', 'NotFoundError',
]


# Exception decorator to catch common gRPC exceptions
def handle_exceptions(f):
    """Custom decorator that re-raises exceptions in terms of dgpy custom exceptions."""
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except grpc._channel._Rendezvous as e:
            # The _Rendezvous error is very verbose, we don't need most of the details.
            if e.code() == grpc.StatusCode.INTERNAL:
                # We use INTERNAL for backend-related errors, so strip code:
                raise GrpcError(e.details())
            elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                raise TimeOutError(e.details())
            elif e.code() == grpc.StatusCode.NOT_FOUND:
                raise NotFoundError(e.details())
            raise GrpcError("{}: {}".format(e.code(), e.details()))
        except Exception:
            raise
    return wrapper

#------------------------------------------------------------------------------------------------------------
# Errors exported by this package
#------------------------------------------------------------------------------------------------------------
class LegacyMessageError(Exception):
    """LegacyMessageError is used to communicate the cause of a failed legacy C Syntropy call"""
    pass

class GrpcError(Exception):
    """GrpcError wraps common gRPC errors"""
    pass

class TimeOutError(Exception):
    """TimeOutError indicates that a command or action did not complete within the given timeout."""
    pass

class NotFoundError(GrpcError):
    """NotFoundError is a GrpcError whose status code indicates that a resource was NOT_FOUND."""
    pass
