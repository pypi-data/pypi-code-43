#!/usr/bin/env python
"""Basic logging utilities"""
import sys, os
import logging
import logging.handlers

__all__ = ['configure_logging']

_ERROR_LOG = os.environ.get('DJANGO_ERROR_LOG', '/var/log/django.log')
_USE_SYSLOG = os.environ.get("DJANGO_USE_SYSLOG", False)

def configure_logging(logger, level=logging.INFO, error_log=_ERROR_LOG, 
    enable_syslog=_USE_SYSLOG):

    if enable_syslog:
        handler = logging.handlers.SysLogHandler(address='/dev/log')
    else:
        handler = logging.FileHandler(error_log)
        
    log = logging.getLogger(logger)
    log.setLevel(level)
    log.addHandler(handler)

    return log

