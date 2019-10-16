# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
import os
import json


def get_dict_from_json(filename):
    if os.path.isfile(filename):
        return json.load(open(filename, "r"), encoding="utf8")
    else:
        print(filename, " doesn't exist")
        return dict()
