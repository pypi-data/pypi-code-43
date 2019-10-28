# -*- coding: utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler

def get_logger(config, **kwargs):
    """Implements a customized logger."""

    # log setting
    # ------------------------------------------------------- #
    name = config.get('application-name')
    logger = logging.getLogger(name)

    # avoid multiple initializations
    if not logger.handlers:

        logging_config = config.get('logging')

        logfile = logging_config.get('filename')
        max_size = logging_config.get('max-size')

        log_level = kwargs.get('level') or logging_config.get('level')

        streaming = kwargs.get('streaming') or False

        file_log_formatter = logging.Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        file_log_handler = RotatingFileHandler(logfile, mode='a', maxBytes=max_size, backupCount=4, encoding='utf-8')
        file_log_handler.setFormatter(file_log_formatter)

        logger.addHandler(file_log_handler)

        if streaming:

            stream_log_formatter = logging.Formatter('%(asctime)s : %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

            stream_log_handler = logging.StreamHandler()
            stream_log_handler.setFormatter(stream_log_formatter)

            logger.addHandler(stream_log_handler)

        logger.setLevel(log_level)

    return logger
