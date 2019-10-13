__version__ = "5.0.4"

import logging

logging.basicConfig()
logger = logging.getLogger("zuper-commons")
logger.setLevel(logging.DEBUG)

logging.info(f"zuper-commons {__version__}")
