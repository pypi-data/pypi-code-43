"""Logging for DTOne Python projects.

This library mimics the API of standard library API
with several differences:

- there is only one singleton Logger (for a service)
- the Logger must be initialized before using this library
- the logging methods/functions accept keyword arguments that are converted
  to `extra` automatically
- the Logger uses MDC, allowing to have default `extra`s stacked
- the default Formatter attached to the Logger, formats messages into JSONs
  for LogStash

Example:

>>> from python_logger import initialize, debug
>>> initialize("my service", log_level="DEBUG")
>>> debug("First message from my service", answer=42)

"""

import contextlib

from .logger import get_logger, initialize

__all__ = [
    "get_logger",
    "initialize",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "log",
    "add_mdc",
]


def debug(message, *args, **kwargs):
    get_logger().debug(message, *args, **kwargs)


def info(message, *args, **kwargs):
    get_logger().info(message, *args, **kwargs)


def warning(message, *args, **kwargs):
    get_logger().warning(message, *args, **kwargs)


def error(message, *args, **kwargs):
    get_logger().error(message, *args, **kwargs)


def critical(message, *args, **kwargs):
    get_logger().critical(message, *args, **kwargs)


def log(level, message, *args, **kwargs):
    get_logger().log(level, message, *args, **kwargs)


@contextlib.contextmanager
def add_mdc(**kwargs):
    with get_logger().add_mdc(**kwargs):
        yield


del contextlib
