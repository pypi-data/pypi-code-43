import logging
import os
from algomax_common.messages import CLASS_IS_SINGLETON
from .json_log_handler import JSONLogHandler
from .json_log_formatter import JSONLogFormatter
from logquacious.backport_configurable_stacklevel import patch_logger
error_logger = logging.getLogger('error-log')
error_logger.__class__ = patch_logger(error_logger.__class__)


DEFAULT_ERROR_LOG_NAME = 'error.json'


class ErrorLogger:
    """
    custom error logger
    this class is singleton
    """

    shared = None

    def __init__(self):
        if ErrorLogger.shared is not None:
            raise Exception(CLASS_IS_SINGLETON.format('ErrorLogger'))
        else:
            ErrorLogger.shared = self

        self.logger = None

    @staticmethod
    def init(path):
        """
        static method for initialize the singleton instance
        :param path: log directory
        """
        if ErrorLogger.shared is not None:
            return

        ErrorLogger()

        ErrorLogger.shared.logger = error_logger
        ErrorLogger.shared.logger.setLevel(logging.ERROR)

        json_file_handler = JSONLogHandler(os.path.join(path, DEFAULT_ERROR_LOG_NAME))

        file_formatter = JSONLogFormatter()

        json_file_handler.setFormatter(file_formatter)

        ErrorLogger.shared.logger.addHandler(json_file_handler)
