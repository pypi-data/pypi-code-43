import logging
import sys


def get_logger(name: str = "deploy.logger", level: int = 1):
    _logger = logging.getLogger(name)
    log_formatter = logging.Formatter('%(levelname)s\t%(asctime)s\t%(name)20s:\t%(message)s')

    if len(_logger.handlers) == 0:
        ch = logging.StreamHandler(sys.stderr)
        ch.setFormatter(log_formatter)
        _logger.addHandler(ch)

    log_level = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }.get(level, logging.DEBUG)

    _logger.setLevel(log_level)
    return _logger

