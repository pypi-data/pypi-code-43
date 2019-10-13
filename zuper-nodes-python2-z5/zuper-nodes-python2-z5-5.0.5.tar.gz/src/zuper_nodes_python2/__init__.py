import logging

__version__ = '5.0.5'

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.info('zn-p2 %s' % __version__)

from .imp import *
from .outside import *
