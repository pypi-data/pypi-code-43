from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object
from typing import Any
from typing import Dict
from typing import Optional


class DatastoreOperation(object):
    def __init__(self, name     , done      ,
                 metadata                           = None,
                 error                 = None,
                 response                           = None)        :
        self.name = name
        self.done = done

        self.metadata = metadata
        self.error = error
        self.response = response

    @classmethod
    def from_repr(cls, data                )                        :
        return cls(data['name'], data['done'], data.get('metadata'),
                   data.get('error'), data.get('response'))

    def to_repr(self)                  :
        return {
            'done': self.done,
            'error': self.error,
            'metadata': self.metadata,
            'name': self.name,
            'response': self.response,
        }
