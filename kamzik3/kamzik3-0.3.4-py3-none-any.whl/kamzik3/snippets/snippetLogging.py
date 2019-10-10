import logging
import sys

# Base formatter for logging.
import traceback
from logging.handlers import TimedRotatingFileHandler

base_log_formatter = logging.Formatter('%(asctime)s, %(name)s, %(levelname)s, %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def set_file_handler(logger, log_output_dir, formatter=base_log_formatter):
    handler = logging.FileHandler(log_output_dir)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def set_rotating_file_handler(logger, log_output_dir, formatter=base_log_formatter):
    handler = TimedRotatingFileHandler(log_output_dir, when="midnight")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler


def get_console_handler(log_level=logging.DEBUG, formatter=base_log_formatter):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    return console_handler


def set_sys_exception_handler(logger):
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception


def print_exception():
    print(traceback.format_exc())
