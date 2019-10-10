import logging
import sys
from traceback import TracebackException

from .filters import AddContextualFieldFilter, MaskPasswordsInLogs
from .formatters import JSONFormatter, ConsoleFormatter
from .utils import _sanitize_stacktrace_for_json_fields


def _uncaught_exception_logger(
    type: BaseException, exc: Exception, traceback: TracebackException
):
    exception_string = _sanitize_stacktrace_for_json_fields(type, exc, traceback)
    # raise to root logger where it will be consumed by the formatter attached to our handler
    logging.getLogger().error(exception_string)


def configure_logging(
    logger_name: str, level: str, log_format: str = "json"
) -> logging.Logger:
    root_logger = logging.getLogger()
    root_logger.addHandler(logging.StreamHandler())
    root_logger.setLevel(level)

    assert root_logger.hasHandlers()
    for handler in root_logger.handlers:
        if log_format != "console":
            handler.setFormatter(JSONFormatter())
        else:
            handler.setFormatter(ConsoleFormatter())
        handler.addFilter(MaskPasswordsInLogs())
        handler.addFilter(AddContextualFieldFilter("service", logger_name))

    sys.excepthook = _uncaught_exception_logger

    return logging.getLogger(logger_name)
