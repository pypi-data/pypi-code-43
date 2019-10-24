#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: help.py
# Author: lmxia
# Mail: xialingming@gmail.com
#############################################


def sum(*values):
    s = 0
    for v in values:
        i = int(v)
        s = s + i
    print s


def output():
    print 'http://xiaoh.me'