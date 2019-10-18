""" Snitch, keylogger and more """

__version__ = "0.4.1"
__author__ = "Grégory Millasseau"

from tempfile import gettempdir

LOG_LEVELS = ['CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
DEFAULT_LOG_LEVEL = 'DEBUG'
DEFAULT_LOG_FILE = '{}/snitch.log'.format(gettempdir())
FILE_VERSION = "0.3"
