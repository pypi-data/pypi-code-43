#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Closable is a concept of a python object which supports the close operation
"""


def is_resource(thing):
    """
    Checks if a given object or type adheres to the closable concept
    :type thing: object or type
    :rtype: bool
    """
    return hasattr(thing, "close") and hasattr(thing.close, "__call__")
