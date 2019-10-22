#!/usr/bin/python3.7
"""
Copyright (C) 2019 Reinventing Geospatial, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>,
or write to the Free Software Foundation, Inc., 59 Temple Place -
Suite 330, Boston, MA 02111-1307, USA.

Author: Jenifer Cochran, Reinventing Geospatial Inc (RGi)
Date: 2019-19-9
Credits:
Version:
"""
from nsg.rgi.common.coordinate import Coordinate


class Tile:  # pylint: disable=R0903
    """Represents a single tile (raster or vector) on a map."""

    def __init__(self,
                 coordinate: Coordinate,
                 source: bytes):
        """
        Constructor
        :param coordinate: the position the tile is on the map.
        :type coordinate: Coordinate
        :param source: the source data.
        :type source: bytearray
        """
        self.coordinate = coordinate
        self.source = source
