#! /usr/bin/env python
# coding: utf-8

import sys
import logging

__author__ = '鹛桑够'


logger = logging.getLogger("jy_cli")
if len(logger.handlers) <= 0:
    sh = logging.StreamHandler(sys.stdout)
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)