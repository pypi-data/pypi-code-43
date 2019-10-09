import os

from .access_logger import AccessLogger
from .error_logger import ErrorLogger

from algomax_common.messages import INVALID_LOG_PATH, CLASS_IS_SINGLETON
from algomax_common.terminal import FontColor


DEFAULT_LOG_PATH = 'logs'


class AMLogger:
    """
    custom json logger
    this class is singleton
    """
    shared = None

    # default log path
    path = DEFAULT_LOG_PATH

    def __init__(self):
        if AMLogger.shared is not None:
            raise Exception(CLASS_IS_SINGLETON.format('AMLogger'))
        else:
            AMLogger.shared = self

    @staticmethod
    def init(path=DEFAULT_LOG_PATH):
        """
        static method for initialize the singleton instance
        :param path: path of logs directory
        """
        if AMLogger.shared is not None:
            return

        AMLogger()
        AMLogger.path = path

        # check if log directory exists
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError:
                print(FontColor.failed(INVALID_LOG_PATH))
                exit(0)

    def get_error_logger(self):
        """
        get error logger instance
        :return: ErrorLogger instance
        """
        ErrorLogger.init(AMLogger.path)
        return ErrorLogger.shared.logger

    def get_access_logger(self):
        """
        get access logger instance
        :return: AccessLogger instance
        """
        AccessLogger.init(AMLogger.path)
        return AccessLogger.shared.logger

    def __error(self, message: str, extra: dict):
        """
        log an error
        :param message: error message
        :param extra: extra params which must be logged
        """
        error_logger = self.get_error_logger()
        if extra is not None and extra.keys():
            error_logger.error(message, extra={'props': extra}, stacklevel=3)
        else:
            error_logger.error(message, stacklevel=3)

    def __info(self, message: str, extra: dict):
        """
        log an info message
        :param message: info message
        :param extra: extra params which must be logged
        """
        access_logger = self.get_access_logger()
        if extra is not None and extra.keys():
            access_logger.info(message, extra={'props' : extra}, stacklevel=3)
        else:
            access_logger.info(message, stacklevel=3)

    @staticmethod
    def error(message: str, extra: dict = {}):
        """
        a static method for calling the AMLogger instance error method
        :param message: error message
        :param extra: extra params which must be logged
        """
        AMLogger.shared.__error(message, extra)

    @staticmethod
    def info(message: str, extra: dict = {}):
        """
        a static method for calling the AMLogger instance info method
        :param message: info message
        :param extra: extra params which must be logged
        """
        AMLogger.shared.__info(message, extra)
