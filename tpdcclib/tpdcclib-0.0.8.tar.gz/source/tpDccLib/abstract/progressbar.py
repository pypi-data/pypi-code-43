#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains abstract definition of basic DCC progress bar
"""

from tpPyUtils import decorators


class AbstractProgressBar(object):

    inc_value = 0

    def __init__(self, *args, **kwargs):
        self.progress_ui = None

    @decorators.abstractmethod
    def set_count(self, count_number):
        pass

    @decorators.abstractmethod
    def get_count(self):
        return 0

    @decorators.abstractmethod
    def status(self, status_str):
        pass

    @decorators.abstractmethod
    def end(self):
        pass

    @decorators.abstractmethod
    def break_signaled(self):
        pass

    def inc(self, inc=1):
        self.__class__.inc_value += inc
