__version__ = "5.0.2"

import logging

logging.basicConfig()
logger = logging.getLogger("zc")
logger.setLevel(logging.DEBUG)

logging.info(f"zc {__version__}")
