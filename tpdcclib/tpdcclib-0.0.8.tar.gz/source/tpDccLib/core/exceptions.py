#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains consts exception used by libraries
"""

from __future__ import print_function, division, absolute_import


class DccError(Exception):
    pass


class NoMatchFoundError(DccError):
    pass


class NoObjectFoundError(DccError):
    pass
