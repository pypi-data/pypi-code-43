"""Various handlers for clalogger

They all takes logger, formatter and level as constructors arguments, and are
automatically associated with the formatter, the logger and the level

Note
----
If level is not provided, the level of the logger will be used
"""

from ._constants import Level

import logging
import logging.handlers
import sys


def _configureHandler(logger, handler, formatter, level):
    """Configures the handler

    #. Sets the level to the given one or, if None, to the logger's level
    #. Sets the formatter to the given one
    #. Adds this handler to the logger

    It is called by internally by this package's handler
    """
    if level is None:
        handler.setLevel(logger.level)
    else:
        if isinstance(level, Level):
            level = level.value
        handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class StderrHandler(logging.StreamHandler):
    """Logging to standard error

    This is a logging.Handler, with associated formatter and level.
    This handler will be added to the logger
    """

    def __init__(self, logger, formatter, level=None):
        """Constructor

        Parameters
        ----------
        logger: logging.Logger
            the logger which will use this; it will be added
        formatter: logging.Formatter
            the formatter used by this handler
            Can be a logging.Formatter or any child class, including formatters
            provided in this package
        level: Level or int or str or None
            the level to be applied to this formatter
            If None, we will use the logger level
            If Level, we will use the enum value
            If int or str, we use it directly for logging level; this includes
            the logging module's constants (e.g. logging.ERROR)
        """
        logging.StreamHandler.__init__(self, stream=sys.stderr)
        _configureHandler(logger, self, formatter, level)


class MidnightFileHandler(logging.handlers.TimedRotatingFileHandler):
    """Logging to a file which rotates every day at midnight

    See Also
    --------
    StderrHandlder
    """

    def __init__(self, logger, fileName, formatter, level=None):
        """Constructor

        See Also
        --------
        StderrHandlder's constructor
        """
        logging.handlers.TimedRotatingFileHandler.__init__(
            self, fileName, interval=1, when='midnight'
        )
        _configureHandler(logger, self, formatter, level)


class StandardFileHandler(logging.FileHandler):
    """Logging to a file which rotates every day at midnight

    See Also
    --------
    StderrHandlder
    """

    def __init__(self, logger, fileName, formatter, level=None):
        """Constructor

        See Also
        --------
        StderrHandlder's constructor
        """
        logging.FileHandler.__init__(
            self, fileName
        )
        _configureHandler(logger, self, formatter, level)
