__version__ = "3.0.4"

import logging

logging.basicConfig()
logger = logging.getLogger("zc")
logger.setLevel(logging.DEBUG)

logging.info(f"zc {__version__}")
