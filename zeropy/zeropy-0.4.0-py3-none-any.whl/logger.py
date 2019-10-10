#!/usr/bin/python

import logging
import logging.config

def setup(path, logger_name):
    logging.config.fileConfig(path)
    logger = logging.getLogger(logger_name )
    return logger