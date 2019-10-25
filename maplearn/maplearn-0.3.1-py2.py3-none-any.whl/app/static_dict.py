# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 20:51:38 2017

source (to create an inherited class from dict):
https://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict

@author: thomas_a
"""
from collections import Mapping

class StaticDict(Mapping):
    """
    "Static" dictionnary: keys are given during initialization and only values
    can be updated later
    
    *args (str): keys to store in the dictionnary (without any value -> None)
    **kwargs (str) : (keys, values) to put in the dictionnary
    """
    __class__ = dict
    def __init__(self, *args, **kwargs):
        self.__dict__ = kwargs   # make a copy
        for i in args:
            self.__dict__.__setitem__(i, None)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        if key not in self.keys():
            raise KeyError("%s is an unavailable key" % str(key))
        self.__dict__[key] = item

    def __len__(self):
        return len(self.__dict__)

    def __iter__(self):
        return iter(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)
    
    def __hash__(self):
        return hash(self.__dict__.items())
    
    def __eq__(self, dict_):
        return dict(self.__dict__) == dict_
