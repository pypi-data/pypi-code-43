import logging


def get_logger(level=0):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger = logging.getLogger(__package__)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
