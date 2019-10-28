#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Used for packaging
name = "Polycephaly"

# Polycephaly core
from .application import Application
from .process import Process

# Logging
from logbook import Logger
from polycephaly.log import logger_group
logger = Logger( __loader__.name )
logger_group.add_logger( logger )
