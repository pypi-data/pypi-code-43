# -*- coding: utf-8 -*-
# @Author  : Gloo
# @time    : 2019/9/15 11:11
# @File    : test2.py
# @Software: PyCharm


class DictObject:
    def __init__(self, _dict):
        # if isinstance(_dict, dict):
        #     self.__dict__['_dict'] = _dict
        # else:
        #     self.__dict__['_dict'] = {}
        self._dict = d

    def __getattr__(self, item):
        try:
            return self._dict[item]
        except KeyError:
            return AttributeError(f"'DictObject' object has no attribute '{item}'")

    def __setattr__(self, key, value):
        print(key, value)


d = {"name": "cai", "age": 18}
dobj = DictObject(d)
print(dobj.__dict__)
print(dobj.name)
