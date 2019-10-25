#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.4'

from .logger import setup_logger
logger = setup_logger()

from . import utils

from .setupper import Setupper