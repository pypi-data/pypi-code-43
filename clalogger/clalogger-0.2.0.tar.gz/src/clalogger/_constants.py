"""Various constants

They are either constants or enums
"""

import enum
import logging


class Level(enum.Enum):
    """Logging level as enum.

    The values *are* the corresponding constants in the logging module (so, for
    example, `Level.debug` = `logging.DEBUG`)
    """
    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL
