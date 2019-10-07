"""Logging configuration."""

import logging

__all__ = ["logger", "set_verbose"]

# Name the logger after the package.
logger = logging.getLogger(__package__)


def set_verbose(verbose: bool, debug: bool = False):
    """Set the logging level to INFO when VERBOSE"""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)

    try:
        import coloredlogs
        if debug:
            coloredlogs.install(level="DEBUG")
        elif verbose:
            coloredlogs.install(level="INFO")
    except ImportError:
        pass
