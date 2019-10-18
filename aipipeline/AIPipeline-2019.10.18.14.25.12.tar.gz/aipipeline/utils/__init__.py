#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = '__init__.py'
__author__ = 'JieYuan'
__mtime__ = '2019-05-31'
"""
import socket


def ifelse(dev, prod):
    return dev if socket.gethostname() == 'yuanjie-Mac.local' else prod
