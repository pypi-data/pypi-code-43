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


class BoundingBox:  # pylint: disable=R0903
    """Represents a geographic bounding area."""

    def __init__(self, min_x: [float, None], max_x: [float, None], min_y: [float, None], max_y: [float, None]):
        """
        Constructor
        :param min_x: Bounding box minimum easting or longitude for all content
        :type min_x: float

        :param min_y: Bounding box minimum northing or latitude for all content
        :type min_y: float

        :param max_x: Bounding box maximum easting or longitude for all content
        :type max_x: float

        :param max_y: Bounding box maximum northing or latitude for all content
        :type max_y: float
        """
        if min_x is not None and max_x is not None:
            assert min_x <= max_x, "x_min value cannot be greater than x_max"
        if min_y is not None and max_y is not None:
            assert min_y <= max_y, "y_min value cannot be greater than y_max"
        self.x_min = min_x
        self.x_max = max_x
        self.y_min = min_y
        self.y_max = max_y
