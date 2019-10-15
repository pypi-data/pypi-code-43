import logging
import adapay
from fishbase.fish_logger import logger


def log_info(info):
    if logging.INFO == adapay.log_level:
        logger.info(adapay.log_tag + '{}'.format(info))


def log_warning(warning_info):
    if adapay.log_level in [logging.INFO, logging.WARNING]:
        logger.warning(adapay.log_tag + '{}'.format(warning_info))


def log_error(error_info):
    if adapay.log_level in [logging.INFO, logging.WARNING, logging.ERROR]:
        logger.error(adapay.log_tag + '{}'.format(error_info))
