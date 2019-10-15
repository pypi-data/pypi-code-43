from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object
from typing import Any
from typing import Dict


# https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/runQuery#Projection
class Projection(object):
    def __init__(self, prop     )        :
        self.prop = prop

    def __eq__(self, other     )        :
        if not isinstance(other, Projection):
            return False

        return bool(self.prop == other.prop)

    def __repr__(self)       :
        return str(self.to_repr())

    @classmethod
    def from_repr(cls, data                )                :
        return cls(prop=data['property']['name'])

    def to_repr(self)                  :
        return {
            'property': {'name': self.prop},
        }
