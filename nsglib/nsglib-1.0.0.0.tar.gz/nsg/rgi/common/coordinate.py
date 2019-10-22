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


class Coordinate:  # pylint: disable=R0903
    """Coordinate the represents a x and y position on a map at a certain zoom_level."""

    def __init__(self,
                 x_coordinate: float,
                 y_coordinate: float,
                 zoom_level: int):
        """
        Constructor
        :param x_coordinate: x or column position on a map.
        :type x_coordinate: float or int
        :param y_coordinate: y or row position on a map.
        :type y_coordinate: float or int
        :param zoom_level: z or zoom level on a map.
        :type zoom_level: int
        """
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.zoom_level = zoom_level
