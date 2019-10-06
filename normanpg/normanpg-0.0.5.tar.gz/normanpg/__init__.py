#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: normanpg
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This is a set of modest utilities that may be helpful when talking to
PostgreSQL.
"""
from .pg import connect, execute, execute_rows, execute_scalar
from .version import __version__, __release__
