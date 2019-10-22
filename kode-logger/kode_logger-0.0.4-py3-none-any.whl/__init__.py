import logging
import sys

import kode_logger.formatters

name = 'kode_logger'


def create_json(context: str) -> logging.Logger:
    logger = logging.getLogger(context)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(kode_logger.formatters.JSONFormatter())

    logger.handlers = [handler]

    return logger
