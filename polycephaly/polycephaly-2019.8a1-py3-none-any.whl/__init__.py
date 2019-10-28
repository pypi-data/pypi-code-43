#!/usr/bin/env python -u
# -*- coding: utf-8 -*-

# Used for packaging
name = "Polycephaly"

# Polycephaly
from .core.application import Application
from .core.process import Process

# Logging
from .log import logger_group
