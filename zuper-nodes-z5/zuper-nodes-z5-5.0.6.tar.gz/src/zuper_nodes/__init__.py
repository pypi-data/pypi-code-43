__version__ = '5.0.6'

from .col_logging import logging
logger = logging.getLogger('zuper-nodes')
logger.setLevel(logging.DEBUG)
logger.info(f'zuper-nodes {__version__}')

from .language import *

from .language_parse import *
from .language_recognize import *

from .structures import  *
