# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import highcompress
import base64


class Compressed(object):
    @staticmethod
    def from_file(cls,path,path2=""):
        if(path2==""):
            path2=path
        with open(path, "rb") as imageFile:
            str = base64.b64encode(imageFile.read())
        return cls.shrink_high(str,path2)

    @staticmethod
    def shrink_high(cls,data,path2):
        if not cls.apikey:
            return ('Provide an API key with highcompress.key = ...')
        else:
            response = cls.request(cls.apikey,data,path2)

        return response
