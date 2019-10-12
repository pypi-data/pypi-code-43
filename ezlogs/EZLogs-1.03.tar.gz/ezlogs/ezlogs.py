import logging

LOG_LEVELS = {
    'debug': 10,
    'info': 20,
    'warn': 30,
    'error': 40,
}

class Logger(object):

    def __init__(self, file_name=None, file_level='info', console_level='debug'):

        assert console_level in LOG_LEVELS.keys(), 'Invalid console logging level'

        if file_name is not None:
            assert file_level in LOG_LEVELS.keys(), 'Invalid file logging level'

        # Store our log level so we can look it up later
        self.file_log_level = LOG_LEVELS[file_level]
        self.console_log_level = LOG_LEVELS[console_level]

        # Set up overall logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.console_log_level)

        log_format = '%(asctime)s [%(levelname)s] %(message)s'
        date_format = '%Y-%m-%dT%H:%M:%S'
        fmt = logging.Formatter(log_format, datefmt=date_format)

        # Set up console logging
        ch = logging.StreamHandler()
        ch.setLevel(self.console_log_level)
        ch.setFormatter(fmt)
        self.logger.addHandler(ch)

        # Set up file logging (if a file name was specified)
        if file_name:
            fh = logging.FileHandler(file_name)
            fh.setLevel(self.file_log_level)
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)


    def info(self, msg):
        self.logger.info(msg)


    def debug(self, msg):
        self.logger.debug(msg)


    def warn(self, msg):
        self.logger.warn(msg)


    def error(self, msg):
        self.logger.error(msg)
