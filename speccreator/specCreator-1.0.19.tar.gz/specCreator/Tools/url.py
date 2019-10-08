#!/usr/bin/env python
# -*- coding=utf-8 -*-

import urllib
from formatter import Formatter
from commonFuncs import *

class URL(object):
    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = URL()
        return cls.__instance

    def isURL(self, URL):
        """
        判断URL是否合法
        :param URL: 提供的URL
        :return: 是否合法
        """
        legalURL = matchList(
            r"^(?:([A-Za-z]+):)?(\/{0,3})([0-9.\-A-Za-z]+)(?::(\d+))?(?:\/([^?#]*))?(?:\?([^#]*))?(?:#(.*))?$", URL)
        if legalURL:
            return True
        else:
            return False

    def URLProtocol(self, URL):
        # http://www.ahlinux.com:8001/test
        protocol, s1 = urllib.splittype(URL)
        # ('http', '//www.ahlinux.com:8001/test')
        return protocol, s1

    def URLPath(self, URL):
        protocol, s1 = self.URLProtocol(URL)
        hostAndPort, path = urllib.splithost(s1)
        # ('www.ahlinux.com:8001', '/test')
        return hostAndPort, path

    def URLHostAndPort(self,URL):
        # type: () -> (str, str)
        hostAndPort, path = self.URLPath(URL)
        host, port = urllib.splitport(hostAndPort)
        # ('www.ahlinux.com', '8001')
        return host, port

    def getUrl(self, content=""):
        content = content.replace("\'","").replace("\"","")
        list = matchList("[a-zA-z]+://[^\s]*", content)
        return list