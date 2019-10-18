#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyraii.resource_concept import is_resource


class CloseFunctor(object):
    """
    Given the semantics of "close" to a function.
    """

    def __init__(self, on_close):
        self._on_close = on_close

    def close(self):
        self._on_close()


assert is_resource(CloseFunctor(lambda: None))
