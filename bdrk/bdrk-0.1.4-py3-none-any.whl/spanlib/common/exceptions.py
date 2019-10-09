import logging
from asyncio import AbstractEventLoop
from logging import Logger, getLogger
from typing import Callable, Dict, Optional


class SpanError(Exception):
    """Span exception.

    NOTE:
    - `status_code`, `resp_message`, and `resp_details` will be used to populate the response that
      the end user receives.
    - `status_code` and `resp_message` are completely determined by the error type.
    - `resp_details` is an optional custom message that is shown to the end user together
      with `resp_message`. It is a keyword-only argument to make explicit that we are passing
      info to the end user.
    - `debug_message` will be used to initialise the base Exception class. We deliberately
      restrict the `SpanError` interface to allow up to one positional argument (v.s. using
      `*args`) in order to align with suggested practice. (c.f.
      https://www.python.org/dev/peps/pep-0352/, especially section on "retracted-ideas")
      At the same time, we do not require this argument to be keyword-only, so that usage can
      remain consistent with built-in exceptions.

    Example usage:
    ```
    raise SpanError(debug_message="My message")  # OK
    raise SpanError("My message")                # OK - equivalent to above

    raise SpanError("My message", resp_details="Details")  # OK
    raise SpanError("My message", "Details")               # Not OK - resp_details is keyword-only
    ```

    :param str debug_message: Debug message, defaults to "".
    :param str resp_details: Response additional details, defaults to "".

    :cvar int log_level: Log level.
    :cvar str status_code: Response status code.
    :cvar str message: Response message.
    :ivar str resp_details: Response additional details.
    """

    def __init__(self, debug_message: str = "", *, resp_details: str = ""):
        super().__init__(debug_message)
        self.debug_message = debug_message
        self.resp_details = resp_details

    def __str__(self):
        return f"{self.resp_message} details={self.resp_details}, debug={self.debug_message}"

    resp_message = "Error encountered."
    status_code = 500
    log_level = logging.DEBUG


class ConfigInvalidError(SpanError):
    resp_message = "Config invalid."
    status_code = 422


class SchemaNotFoundError(SpanError):
    resp_message = "Bedrock hcl schema file not found."
    status_code = 500
    log_level = logging.ERROR


class DataClassConversionError(SpanError):
    log_level = logging.ERROR


class IOError(SpanError):
    resp_message = "IO error."
    status_code = 500
    log_level = logging.ERROR


class FatalError(Exception):
    pass


def fatal_error_handler(
    func: Callable[[], None], logger: Optional[Logger] = None
) -> Callable[[AbstractEventLoop, Dict], None]:
    """Returns asyncio event loop exception handler that logs the exception context
    and calls func if exception represents a FatalError.

    :param Callable[[], None] func: Function to call on FatalError.
    :param Logger, optional logger: Exception logger, defaults to root logger.
    :return Callable[[AbstractEventLoop, Dict], None]: Asyncio event loop exception handler.
    """
    _logger = logger or getLogger()

    def handler(loop: AbstractEventLoop, context: Dict):
        message = context.get("message")
        exc: Optional[Exception] = context.get("exception")

        is_fatal_error = isinstance(exc, FatalError)

        error_type = "FATAL ERROR" if is_fatal_error else "Error"
        _logger.error(
            f"{error_type} in event loop: message={message}, exc={exc}",
            exc_info=exc,
            extra={"context": context},
        )

        if is_fatal_error:
            func()

    return handler
