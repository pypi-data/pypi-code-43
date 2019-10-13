__version__ = "5.0.6"

import logging

logging.basicConfig()
logger = logging.getLogger("zuper-commons")
logger.setLevel(logging.DEBUG)

logger.info(f"zuper-commons {__version__}")
