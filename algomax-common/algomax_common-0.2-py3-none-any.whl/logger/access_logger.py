import logging, os
from .json_log_formatter import JSONLogFormatter
from algomax_common.messages import CLASS_IS_SINGLETON
from .json_log_handler import JSONLogHandler
from logquacious.backport_configurable_stacklevel import patch_logger
access_logger = logging.getLogger('info-log')
access_logger.__class__ = patch_logger(access_logger.__class__)

DEFAULT_ACCESS_LOG_NAME = 'info.json'


class AccessLogger:
    """
    custom access logger
    this class is singleton
    """

    shared = None

    def __init__(self):
        if AccessLogger.shared is not None:
            raise Exception(CLASS_IS_SINGLETON.format('AccessLogger'))
        else:
            AccessLogger.shared = self

        self.logger = None

    @staticmethod
    def init(path):
        """
        static method for initialize the singleton instance
        :param path: log directory
        """
        if AccessLogger.shared is not None:
            return

        AccessLogger()

        AccessLogger.shared.logger = access_logger
        AccessLogger.shared.logger.setLevel(logging.INFO)

        json_file_handler = JSONLogHandler(os.path.join(path, DEFAULT_ACCESS_LOG_NAME))

        file_formatter = JSONLogFormatter()

        json_file_handler.setFormatter(file_formatter)

        AccessLogger.shared.logger.addHandler(json_file_handler)
