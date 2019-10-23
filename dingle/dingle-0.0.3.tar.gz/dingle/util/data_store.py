# -*- coding: utf-8 -*-
'''
Provide basic data store.
'''

class DictStore(dict):
    def set(self, key, value, **kw):
        self[key] = value

