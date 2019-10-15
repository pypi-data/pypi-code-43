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

from gcloud.rest.datastore.constants import Direction


# https://cloud.google.com/datastore/docs/reference/data/rest/v1/projects/runQuery#PropertyOrder
class PropertyOrder(object):
    def __init__(self, prop     ,
                 direction            = Direction.ASCENDING)        :
        self.prop = prop
        self.direction = direction

    def __eq__(self, other     )        :
        if not isinstance(other, PropertyOrder):
            return False

        return bool(
            self.prop == other.prop
            and self.direction == other.direction)

    def __repr__(self)       :
        return str(self.to_repr())

    @classmethod
    def from_repr(cls, data                )                   :
        prop = data['property']['name']
        direction = Direction(data['direction'])
        return cls(prop=prop, direction=direction)

    def to_repr(self)                  :
        return {
            'property': {'name': self.prop},
            'direction': self.direction.value,
        }
