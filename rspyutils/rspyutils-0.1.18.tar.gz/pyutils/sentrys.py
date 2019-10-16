# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
from raven import Client


class SentryCli(object):
    def __init__(self, dsn):
        if dsn:
            self.client = Client(dsn)
        else:
            raise Exception("Sentry_dsn input error!!!")

    def check_commom_err(self, e):
        self.client.captureException(e)
