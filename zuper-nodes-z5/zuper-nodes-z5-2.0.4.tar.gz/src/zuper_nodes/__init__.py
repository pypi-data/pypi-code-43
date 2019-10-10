__version__ = '2.0.4'

from .col_logging import logging
logger = logging.getLogger('zn')
logger.setLevel(logging.DEBUG)
logger.info(f'zn {__version__}')

from .language import *

from .language_parse import *
from .language_recognize import *

from .structures import  *
