#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-CLI.
# @File         : demo
# @Time         : 2019-07-16 20:38
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 


class Demo:
    """cli A f 1 1000"""

    def __init__(self, q='hi', d={'x': 1, 'y': 2}):
        self.q = q
        print(d)
        for k, v in d.items():
            setattr(self, k, v)
        print(self.x)

    def f(self, x, y):
        return x + 1

    def ff(self, a=''):
        return self.q + ': ' + a

