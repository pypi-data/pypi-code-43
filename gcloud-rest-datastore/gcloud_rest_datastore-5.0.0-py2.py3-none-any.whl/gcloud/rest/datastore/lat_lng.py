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


# https://cloud.google.com/datastore/docs/reference/data/rest/Shared.Types/LatLng
class LatLng(object):
    def __init__(self, lat       , lon       )        :
        self.lat = lat
        self.lon = lon

    def __eq__(self, other     )        :
        if not isinstance(other, LatLng):
            return False

        return bool(
            self.lat == other.lat
            and self.lon == other.lon)

    def __repr__(self)       :
        return str(self.to_repr())

    @classmethod
    def from_repr(cls, data                )            :
        lat = data['latitude']
        lon = data['longitude']
        return cls(lat=lat, lon=lon)

    def to_repr(self)                  :
        return {
            'latitude': self.lat,
            'longitude': self.lon,
        }
