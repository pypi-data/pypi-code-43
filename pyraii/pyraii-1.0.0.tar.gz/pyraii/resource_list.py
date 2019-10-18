#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyraii.close import close_multiple


class ResourcesList(object):
    """
    Assumes ownership for closing a given list of resources IN REVERSE ORDER
    to know why in reverse order see the documentation for `close_multiple`
    """
    def __init__(self, *resources):
        self.resources = resources

    def __iter__(self):
        return iter(self.resources)

    def close(self):
        close_multiple(self.resources)
