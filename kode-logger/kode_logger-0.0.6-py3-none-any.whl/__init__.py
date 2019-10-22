import logging
import sys
from typing import List, Mapping, Optional

import kode_logger.formatters

name = 'kode_logger'


def create_json(context: str, *, tags: Optional[List[str]] = None, extra: Optional[Mapping] = None) -> logging.Logger:
    logger = logging.getLogger(context)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(kode_logger.formatters.JSONFormatter(tags=tags, extra=extra))

    logger.handlers = [handler]

    return logger
