# encoding: utf-8

import json

class Node(object):


    def __init__(self, parent=None, key=None):

        self.parent   = parent
        self.key      = key
        self.value    = 0
        self.children = {}


    def __repr__(self):

        return ', '.join((str(id(self.parent)),
                         str(self.key),
                         str(self.value),
                         json.dumps({
                             k:id(v) for k, v in self.children.items()
                         }, ensure_ascii=False)))
