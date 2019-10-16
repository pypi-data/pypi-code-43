#!/usr/bin/env python
# coding: utf8

import common

from src import daemonlog

#print(daemonlog)
l = daemonlog.Logger("LogTest")
l.debug("Testing logger")
l.debug(u"Testar loggaren åäö")
l.debug("Testar loggaren igen åäö")
