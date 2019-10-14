"""Exceptions thrown by limit function call implementations.

Adapted from https://github.com/sfalkner/pynisher
"""
from automl.client.core.common.constants import ClientErrors
from automl.client.core.common.exceptions import ClientException, ResourceException


class CpuTimeoutException(ResourceException):
    """Exception to raise when the cpu time exceeded."""

    def __init__(self, exception_message=None, target=None):
        """Constructor."""
        message = ClientErrors.EXCEEDED_TIME_CPU if exception_message is None else exception_message
        super().__init__(message, target)


class TimeoutException(ResourceException):
    """Exception to raise when the total execution time exceeded."""

    def __init__(self, exception_message=None, target=None):
        """Constructor.

        :param value: time consumed
        """
        message = ClientErrors.EXCEEDED_TIME if exception_message is None else exception_message
        super().__init__(message, target)


class MemorylimitException(ResourceException):
    """Exception to raise when memory exceeded."""

    def __init__(self, exception_message=None, target=None):
        """Constructor.

        :param value:  the memory consumed.
        """
        message = ClientErrors.EXCEEDED_MEMORY if exception_message is None else exception_message
        super().__init__(message, target)


class SubprocessException(ClientException):
    """Exception to raise when subprocess terminated."""

    def __init__(self, exception_message=None, target=None):
        """Constructor.

        :param message:  Exception message.
        """
        message = ClientErrors.SUBPROCESS_ERROR if exception_message is None else exception_message
        super().__init__(message, target)
