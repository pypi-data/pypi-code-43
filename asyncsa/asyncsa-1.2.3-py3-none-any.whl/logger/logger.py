import logging
import os

def get_logger():
    logger = logging.getLogger(__package__)
    lv = get_logger_level()
    logger.setLevel(lv)
    return logger


def get_logger_level():
    sa = os.getenv('asyncsa')
    result = 10
    if sa == 'CRITICAL':
        result = 50
    elif sa == 'ERROR':
        result = 40
    elif sa == 'WARNING':
        result = 30
    elif sa == 'INFO':
        result = 20
    elif sa == 'DEBUG':
        result = 10
    return result

