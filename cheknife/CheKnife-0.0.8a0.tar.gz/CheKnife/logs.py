import os
from logging.config import dictConfig


class Loggers(object):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            # https://docs.python.org/3/library/logging.html#logrecord-attributes
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'fileLogFormat': {
                'format': '%(asctime)s %(levelname)s [%(module)s] %(message)s %(pathname)s %(lineno)d',
            },
            'consoleLogFormat': {
                'format': '%(asctime)s %(levelname)s [%(module)s]: %(message)s %(pathname)s %(lineno)d'
            },
            'simple': {
                'format': '%(module)s %(levelname)s %(message)s',
            },
        },
        'handlers': {},
        'loggers': {},
        'filters': {},
    }
    DEBUG_LOGGER = {
        'handlers': ['file', 'error_file', 'console'],
        'level': 'DEBUG',
        'propagate': False,
    }
    INFO_LOGGER = {
        'handlers': ['file', 'error_file', 'console'],
        'level': 'INFO',
        'propagate': False,
    }

    def __init__(self, project_name, logs_root='/var/log/', file_max_bytes=5242880, keep_last_files=10, debug=False):
        self.project_name = project_name
        self.logs_root = logs_root
        self.file_max_bytes = file_max_bytes
        self.keep_last_files = keep_last_files
        handlers = {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(logs_root, f'{project_name}.log'),
                'maxBytes': self.file_max_bytes,
                'backupCount': self.keep_last_files,
                'formatter': 'fileLogFormat',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(logs_root, f'{project_name}_errors.log'),
                'formatter': 'fileLogFormat',
                'maxBytes': self.file_max_bytes,
                'backupCount': self.keep_last_files,
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'consoleLogFormat',
            },
        }
        self.add_handlers(handlers)
        if debug:
            self.add_logger('', self.DEBUG_LOGGER)
        else:
            self.add_logger('', self.INFO_LOGGER)

    def add_handlers(self, handlers):
        for name, config in handlers.items():
            self.add_handler(name, config)

    def add_handler(self, name, config):
        self.LOGGING['handlers'].update({name: config})

    def add_logger(self, name, config):
        self.LOGGING['loggers'].update({name: config})

    def add_formatter(self, name, format_string):
        self.LOGGING['formatters'].update({name: format_string})

    def setup(self):
        dictConfig(self.LOGGING)

"""
from CheKnife.logs import Loggers
loggers = Loggers('test', logs_root='/tmp', debug=True)
loggers.add_logger('debug', loggers.DEBUG_LOGGER)
loggers.setup()
import logging
l = logging.getLogger('debug')
l.debug('some message')
"""