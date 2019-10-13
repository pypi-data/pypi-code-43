#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from funity import __name__ as module_name

_logger = None


def _acquire_logger():
    return logging.getLogger(module_name)


def get_logger():
    global _logger

    if not _logger:
        _logger = _acquire_logger()

    return _logger
