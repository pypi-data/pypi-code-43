# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals
import sys
class highcompress(object):

    def __init__(self, module):
        self._module = module
        self._client = None
        self._apikey = None
        self._compression_count = None
        self._apikey = None

    @property
    def key(self):
        return self.apikey

    @key.setter
    def key(self,value):
        self.apikey = value
    # Delegate to underlying base module.
    def __getattr__(self, attr):
        return getattr(self._module, attr)

    def from_file(self, path,path2=""):
        return Compressed.from_file(self,path,path2)

    def shrink_high(self,data,path2):
        return Compressed.shrink_high(self,data,path2)

    def request(self,key,data,path2):
        return Client.request(self,key,data,path2)
    def check_credit(self,key=""):
        return Client.check_credit(self,key)


highcompress = sys.modules[__name__] = highcompress(sys.modules[__name__])

from .compressed import Compressed
from .client import Client
