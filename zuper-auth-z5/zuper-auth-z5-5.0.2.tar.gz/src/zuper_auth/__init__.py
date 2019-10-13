__version__ = '5.0.2'
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.info(f'zuper-auth {__version__}')
