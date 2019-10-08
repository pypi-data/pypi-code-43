#!/usr/bin/env python
# -*- coding=utf-8 -*-


import sys
from formatter import Formatter

class Result(object):

    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = Result()
        return cls.__instance

    def returnError(self, message=""):
        # TODO 清理工作
        self.formatter.format_error(message)
        exit(1)

    def returnSuccess(self, message=""):
        # TODO 清理工作。
        self.formatter.format_info(message)
        exit(0)

