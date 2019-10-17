#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-CLI.
# @File         : cli_example
# @Time         : 2019-07-12 09:52
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


import fire


# fire.Fire(lambda obj: type(obj).__name__)


class Calculator(object):
    """doc"""

    def __init__(self, arg=0):
        self.arg = arg

    def add(self, x, y):
        """add"""
        return x + y

    def multiply(self, x, y):
        """add"""
        return x * y + self.arg

    def get_list(self, x):
        print(type(x))
        return x


def calculator():
    fire.Fire(Calculator)
