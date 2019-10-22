# pylint: disable=no-value-for-parameter
# pylint: disable=too-many-arguments
import copy
import json
import logging
import sys
import traceback
from contextlib import contextmanager
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, Optional


def _merge_dicts(dict1, dict2):
    """
    if the key is in both second overrides the first
    """
    output = copy.deepcopy(dict1)
    for key, value in copy.deepcopy(dict2).items():
        if isinstance(value, dict) and isinstance(dict1.get(key, None), dict):
            output[key] = _merge_dicts(dict1[key], value)
        else:
            output[key] = value
    return output


class LogRecord(logging.LogRecord):
    """Log record keeping `extra` separately."""

    # fmt: off
    def __init__(
            self,
            name,
            level,
            pathname,
            lineno,
            msg,
            args,
            exc_info,
            func=None,
            sinfo=None,
            extra=None
    ):
        super().__init__(name, level, pathname, lineno, msg, args, exc_info, func=func, sinfo=sinfo)
        self.extra = extra
    # fmt: on


class Formatter(logging.Formatter):
    """Formatter producing LogStash-ready JSON strings."""

    LOG_LEVEL_NAMES = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARN",
        "ERROR": "ERROR",
        "CRITICAL": "FATAL",
    }
    """Mapping of python native log levels into DTOne custom loge levels. The mapping is done to
   archive unified log levels across all components and all programming languages.
   """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc)
        output_dict: Dict[str, Any] = {
            "service": record.name,
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            "log_level": Formatter.LOG_LEVEL_NAMES.get(record.levelname, "ERROR"),
            "message": record.getMessage(),
        }
        if isinstance(record, LogRecord):
            output_dict.update(record.extra)
        if record.exc_info:
            exc_type, exc_value, tb_info = record.exc_info
            if exc_type:
                exc_message = getattr(exc_value, "strerror", str(exc_value))
                tb_message = "".join(traceback.format_exception(exc_type, exc_value, tb_info))

                output_dict["exception"] = {
                    "class": exc_type.__name__,
                    "message": exc_message,
                    "stacktrace": tb_message,
                }

        sorted_msg = dict(sorted(output_dict.items(), key=lambda kv: kv[0]))
        return json.dumps(sorted_msg)


class Logger(logging.Logger):
    """Singleton logger with a stackable MDC."""

    _mdc: ContextVar[dict] = ContextVar("logger_context")

    PROTECTED_KEYS = (
        "exc_info",
        "stack_info",
        "level",
        "log_level",
        "message",
        "service",
        "timestamp",
        "exception",
        "extra",
    )
    """Keys that have special meaning either for the API or for the output."""

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        if _LOGGER:
            return _LOGGER
        return super().__new__(cls)

    def __init__(self, service: str):
        if hasattr(self, "name") and self.name != service:
            raise RuntimeError("Cannot reinitialise logger with another service name")
        super().__init__(service)
        Logger._mdc.set({})

    # fmt: off
    def makeRecord(
            self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None
    ):
        extra = _merge_dicts(self.mdc(), extra or {})
        return LogRecord(
            name,
            level=level,
            pathname=fn,
            lineno=lno,
            msg=msg,
            args=args,
            exc_info=exc_info,
            func=func,
            sinfo=sinfo,
            extra=extra,
        )

    def _log(
            self, level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs
    ):  # pylint: disable=arguments-differ
        super()._log(
            level,
            msg,
            args,
            exc_info=exc_info,
            stack_info=stack_info,
            extra=_merge_dicts(kwargs, extra or {}),
        )
    # fmt: on

    def mdc(self) -> dict:
        return self._mdc.get()

    def _push_mdc(self, **kwargs) -> Token:
        for key in kwargs:
            if key in self.PROTECTED_KEYS:
                raise ValueError(f"Cannot add {key} to MDC as it is a protected logging argument.")
        new_mdc = _merge_dicts(Logger._mdc.get(), kwargs)
        return self._mdc.set(new_mdc)

    def _reset_mdc(self, token: Token) -> None:
        """Return the MDC to the previous state."""
        # Removes all keys added after the token
        self._mdc.reset(token)

    @contextmanager
    def add_mdc(self, **kwargs) -> Iterator[None]:
        """Context manager with new MDC merged with the existing one."""
        token = self._push_mdc(**kwargs)
        try:
            yield
        finally:
            self._reset_mdc(token)


_LOGGER: Optional[Logger] = None


def initialize(service: str, log_level=logging.root.level) -> None:
    global _LOGGER  # pylint: disable=global-statement
    if _LOGGER:
        raise RuntimeError("Logger can be initialized only once.")
    current_logger_class = logging.getLoggerClass()
    try:
        logging.setLoggerClass(Logger)
        _LOGGER = logging.getLogger(service)  # type: ignore
        if not isinstance(_LOGGER, Logger):
            raise RuntimeError(f"Logger {service} already initialized with another logger.")

        _LOGGER.setLevel(log_level)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(Formatter())
        _LOGGER.addHandler(handler)
    finally:
        logging.setLoggerClass(current_logger_class)


def get_logger() -> Logger:
    if not _LOGGER:
        raise RuntimeError("Logger not yet set up.")
    return _LOGGER
