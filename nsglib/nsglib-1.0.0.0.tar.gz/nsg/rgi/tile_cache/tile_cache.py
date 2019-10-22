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
from abc import abstractmethod, ABC
from nsg.rgi.tile_cache.tile import Tile  # pylint: disable=W0611
from nsg.rgi.common.coordinate import Coordinate


class AbstractTileCache(ABC):
    """Base class for a tile cache."""

    @abstractmethod
    def add_tile(self, tile: Tile):
        """
        Adds a tile to the tile cache.

        :param tile: the tile to add to the tile cache
        :type tile: Tile
        """
        raise NotImplementedError()

    @abstractmethod
    def get_tile(self, coordinate: Coordinate) -> Tile:
        """
        Retrieves a tile from the tile cache with the coordinates given.

        :param coordinate: the row, column, and zoom level of the tile to retrieve (origin is assumed to be upper left)
        :type coordinate: Coordinate
        :return: returns the tile with the given coordinates
        :rtype: Tile
        """
        raise NotImplementedError()
