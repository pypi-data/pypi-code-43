#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SciExp²-ExpRun provides a framework for easing the workflow of executing
experiments that require orchestrating multiple processes in local and/or remote
machines.

"""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


__version_info__ = (0, 1, 3)
__version__ = ".".join([str(i) for i in __version_info__])

__all__ = [
    "cpu", "files", "kernel", "process", "spur", "util", "wait",
]
