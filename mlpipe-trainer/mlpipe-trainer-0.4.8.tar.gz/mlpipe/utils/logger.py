import logging
import io
import os
import sys
import re
import tensorflow as tf


class MLPipeLogger:
    """Manage logging of MLPipe"""
    _logger_level = logging.DEBUG
    _formatter = logging.Formatter('[%(asctime)s] %(levelname)-10s %(message)s')
    _log_contents = io.StringIO()
    _current_log_file_path = "mlpipe.log"
    _output = ""  # intercepted output from stdout and stderr
    logger = None
    string_handler = None
    file_handler = None
    console_handler = None

    @staticmethod
    def setup_logger():
        """
        Setup logger for StringIO, console and file handler
        """
        if MLPipeLogger.logger is not None:
            print("WARNING: logger was setup already, deleting all previously existing handlers")
            for hdlr in MLPipeLogger.logger.handlers[:]:  # remove all old handlers
                MLPipeLogger.logger.removeHandler(hdlr)

        # Create the logger
        MLPipeLogger.logger = tf.get_logger()
        for hdlr in MLPipeLogger.logger.handlers:
            MLPipeLogger.logger.removeHandler(hdlr)
        MLPipeLogger.logger.setLevel(MLPipeLogger._logger_level)
        MLPipeLogger.logger.propagate = False  # otherwise tensorflow duplicates each mlpipe logging to the console

        # Setup the StringIO handler
        MLPipeLogger._log_contents = io.StringIO()
        MLPipeLogger.string_handler = logging.StreamHandler(MLPipeLogger._log_contents)
        MLPipeLogger.string_handler.setLevel(MLPipeLogger._logger_level)

        # Setup the console handler
        MLPipeLogger.console_handler = logging.StreamHandler(sys.stdout)
        MLPipeLogger.console_handler.setLevel(MLPipeLogger._logger_level)

        # Setup the file handler
        MLPipeLogger.file_handler = logging.FileHandler(MLPipeLogger._current_log_file_path, 'a')
        MLPipeLogger.file_handler.setLevel(MLPipeLogger._logger_level)

        # Optionally add a formatter
        MLPipeLogger.string_handler.setFormatter(MLPipeLogger._formatter)
        MLPipeLogger.console_handler.setFormatter(MLPipeLogger._formatter)
        MLPipeLogger.file_handler.setFormatter(MLPipeLogger._formatter)

        # Add the console handler to the logger
        MLPipeLogger.logger.addHandler(MLPipeLogger.string_handler)
        MLPipeLogger.logger.addHandler(MLPipeLogger.console_handler)
        MLPipeLogger.logger.addHandler(MLPipeLogger.file_handler)

    @staticmethod
    def write(buf):
        """
        Override the write() function for stdout / stderr to intercept it and use mlpipe logger instead
        :param buf: a string passed to stdout
        """
        # For each new line character a seperate log entry should be generated
        # this replicates the stdout / stderr output into the logs
        for i, line in enumerate(buf.splitlines(True)):
            MLPipeLogger._output += line
            if re.match(r'^.*[\r\n]$', line):
                MLPipeLogger.flush()

    @staticmethod
    def flush():
        """
        Override flush method of stdout / stderr
        each time flush is called a new log entry should be generated
        apart from the user calling flush, write() calls flush after each new line character
        """
        # strip and remove \b (backspace) from output string as keras likes to add these a lot
        MLPipeLogger._output = MLPipeLogger._output.strip().replace("\b", "")
        if MLPipeLogger._output != "":
            MLPipeLogger.logger.info(MLPipeLogger._output)
            MLPipeLogger._output = ""

    @staticmethod
    def set_log_file(path, mode: str='a'):
        """
        Set the path of the log file
        :param path: path + name of the new log file
        :param mode: mode e.g. 'a' => append (default), 'w' => write
        """
        MLPipeLogger._current_log_file_path = path
        MLPipeLogger.logger.removeHandler(MLPipeLogger.file_handler)

        MLPipeLogger.file_handler = logging.FileHandler(MLPipeLogger._current_log_file_path, mode)
        MLPipeLogger.file_handler.setLevel(MLPipeLogger._logger_level)
        MLPipeLogger.logger.addHandler(MLPipeLogger.file_handler)

    @staticmethod
    def remove_file_logger():
        """
        Remove the file logger to not write output to a log file
        """
        MLPipeLogger.logger.removeHandler(MLPipeLogger.file_handler)
        if os.path.exists(MLPipeLogger._current_log_file_path):
            os.remove(MLPipeLogger._current_log_file_path)

    @staticmethod
    def get_contents():
        """
        Get current contents of the logger
        :return: list of log strings
        """
        return MLPipeLogger._log_contents.getvalue()

    @staticmethod
    def get_log_file_path() -> str:
        """
        :return: path to the current log file
        """
        return MLPipeLogger._current_log_file_path

    @staticmethod
    def set_level(lvl):
        """
        Set logging level
        :param lvl: logging level
        """
        MLPipeLogger._logger_level = lvl
        MLPipeLogger.setup_logger()

    @staticmethod
    def init():
        """
        Initialize the MLPipe logger, only needed to be called once as it is a static class
        """
        MLPipeLogger.setup_logger()

        # redirect stderr & stdout to logger (implements write method)
        sys.stderr = MLPipeLogger
        sys.stdout = MLPipeLogger

