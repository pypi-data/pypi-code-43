import logging
from rammon.config import LAUNCHED_FROM_SYSTEMD

logger = logging.getLogger("rammon")
logger.setLevel(logging.INFO)


def add_console_handler():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)


if LAUNCHED_FROM_SYSTEMD:
    try:
        from systemd.journal import JournaldLogHandler

        journald_handler = JournaldLogHandler()
        journald_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logger.addHandler(journald_handler)
    except ModuleNotFoundError:
        add_console_handler()
else:
    add_console_handler()
