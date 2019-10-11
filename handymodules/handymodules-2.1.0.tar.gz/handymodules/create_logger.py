__all__ = ['CreateLogger']

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from sys import argv

# getting filename
filename = os.path.basename(argv[0])
# if file has dots in name
tmp_list = filename.split('.')
if len(tmp_list) > 1:
    tmp_list.pop(-1)
    filename = '.'.join(tmp_list)


def _create_logs_dir(inside_folder_name=None):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    if inside_folder_name and not os.path.exists('logs/{}'.format(inside_folder_name)):
        os.mkdir('logs/{}'.format(inside_folder_name))


class CreateLogger(object):
    def __init__(self, logger_name: str = filename,
                 stream_handler: bool = True,
                 file_handler: bool = True,
                 log_filename: str = filename,
                 **kwargs):
        # kwargs
        timed_rotating_file = kwargs.pop('timed_rotating_file', False)
        days_to_keep = kwargs.pop('days_to_keep', 7)
        log_inside_folder = kwargs.pop('log_inside_folder', False)
        if len(kwargs) > 0:
            import warnings
            warnings.warn('Unexpected kwargs - {}'.format(kwargs))
        # create logger
        self._log = logging.getLogger(logger_name)
        self.file_handler = None
        self.cmd_handler = None
        self.loglevel = logging.DEBUG
        # create log format
        self._log_format = None
        self.change_format()
        # creating logs directories and adding file handler
        if file_handler:
            if log_inside_folder:
                _create_logs_dir(log_filename)
                self._logfile_name = '{0}/{0}.log'.format(log_filename)
            else:
                _create_logs_dir()
                self._logfile_name = '{}.log'.format(log_filename)

            self.add_file_handler(timed_rotating_file, days_to_keep)
        # adding stream handler
        if stream_handler:
            self.add_stream_handler()
        # setting level
        self._log.setLevel(self.loglevel)

    def debug(self, debug_message, *args, **kwargs):
        self._log.debug(debug_message, *args, **kwargs)

    def info(self, info_message, *args, **kwargs):
        self._log.info(info_message, *args, **kwargs)

    def warning(self, warning_message, *args, **kwargs):
        self._log.warning(warning_message, *args, **kwargs)

    def error(self, error_message, *args, **kwargs):
        self._log.error(error_message, *args, **kwargs)

    def critical(self, critical_message, *args, **kwargs):
        self._log.critical(critical_message, *args, **kwargs)

    def exception(self, exception_message='', one_line=True, delimiter='|'):
        if one_line:
            import traceback
            exception = delimiter.join(traceback.format_exc().split('\n'))
            self._log.error('{0} {1}{2}'.format(exception_message, delimiter, exception))
        else:
            self._log.exception(exception_message)

    def add_stream_handler(self):
        self.cmd_handler = logging.StreamHandler()
        self.cmd_handler.setLevel(self.loglevel)
        self.cmd_handler.setFormatter(self._log_format)
        self._log.addHandler(self.cmd_handler)

    def add_file_handler(self, timed_rotating_file=False, days_to_keep=7):
        if timed_rotating_file:
            self.file_handler = TimedRotatingFileHandler('logs/{}'.format(self._logfile_name),
                                                         'midnight', 1, days_to_keep, 'UTF-8')
        else:
            self.file_handler = logging.FileHandler('logs/{}'.format(self._logfile_name), encoding='UTF-8')
        self.file_handler.setLevel(self.loglevel)
        self.file_handler.setFormatter(self._log_format)
        self._log.addHandler(self.file_handler)

    def change_level(self, level):
        if level == 'info' or level == 20:
            self.loglevel = logging.INFO
        elif level == 'warning' or level == 30:
            self.loglevel = logging.WARNING
        elif level == 'error' or level == 40:
            self.loglevel = logging.ERROR
        elif level == 'critical' or level == 50:
            self.loglevel = logging.CRITICAL
        else:
            self.loglevel = logging.DEBUG

        if self.file_handler:
            self.file_handler.setLevel(self.loglevel)
        if self.cmd_handler:
            self.cmd_handler.setLevel(self.loglevel)

    def change_format(self, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        self._log_format = logging.Formatter(log_format)
        if self.file_handler:
            self.file_handler.setFormatter(self._log_format)
        if self.cmd_handler:
            self.cmd_handler.setFormatter(self._log_format)

    def get_handlers(self):
        return self._log.handlers
