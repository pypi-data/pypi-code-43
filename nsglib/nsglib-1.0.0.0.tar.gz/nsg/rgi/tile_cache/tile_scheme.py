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
import math
from abc import abstractmethod, ABC
from typing import Tuple

from nsg.rgi.common.bounding_box import BoundingBox


class TileScheme(ABC):  # pylint: disable=R0903
    """
    Mechanism to describe the number of tiles in a tile set, at a given zoom level
    """

    @abstractmethod
    def get_matrix_dimensions(self,
                              zoom_level):
        """
        Calculates the height and width of the tile matrix for a given zoom level.  Returns a tuple where the first
        value is the matrix width and the second value is the matrix height. (matrix_width, matrix_height)

        :param zoom_level: zoom level
        :type zoom_level: int

        :rtype: tuple(int, int)
        """
        raise NotImplementedError()


class ZoomTimesTwo(TileScheme):  # pylint: disable=R0903
    """
    Calculates the tile matrix dimensions by a factor of 2.
    """

    def get_matrix_dimensions(self, zoom_level):
        """
        Calculates the height and width of the tile matrix for a given zoom level.  Returns a tuple where the first
        value is the matrix width and the second value is the matrix height. (matrix_width, matrix_height)

        :param zoom_level: the zoom level of the matrix dimensions needed
        :type zoom_level: int
        :return: Returns a tuple where the first
        value is the matrix width and the second value is the matrix height. (matrix_width, matrix_height)
        :rtype: tuple(int, int)
        """
        two_to_the_zoom = 2 ** zoom_level
        return self.base_matrix_width * two_to_the_zoom, self.base_matrix_height * two_to_the_zoom

    def __init__(self,
                 base_matrix_width,
                 base_matrix_height):
        self.base_matrix_width = base_matrix_width
        self.base_matrix_height = base_matrix_height


def calc_resolutions(bounding_box: BoundingBox,
                     tile_size: Tuple[int, int],
                     zoom_level: int,
                     tile_scheme: TileScheme):
    """
    Returns the pixel_x_size, pixel_y_size given the following values.

    :param tile_scheme: Gives the dimensions of the tile grid given a zoom level
    :type tile_scheme: TileScheme

    :param bounding_box:  The bounds of the data in the CRS coordinates (meters, decimal degrees etc.)
    :type bounding_box: BoundingBox

    :ivar tile_size: the size of each tile in pixel
    :type tile_size: ``int(with), int(height)``

    :param zoom_level: the zoom level to calculate the resolution for
    :type zoom_level: int

    :return: tuple of pixel_x_size and pixel_y_size
    :rtype: tuple(float, float)
    """

    width = float(bounding_box.x_max - bounding_box.x_min)
    height = float(bounding_box.y_max - bounding_box.y_min)

    matrix_width, matrix_height = tile_scheme.get_matrix_dimensions(zoom_level=zoom_level)

    return ((width / float(tile_size[0])) / float(matrix_width)), \
           ((height / float(tile_size[1])) / float(matrix_height))


PIXELS_PER_METER = 0.00028
EARTH_EQUATORIAL_RADIUS_METERS = 6378137.0


def calculate_scale_denominator(zoom_level: int,
                                tile_size_width: int = 256,
                                bounds_meters_width: float = 2 * math.pi * EARTH_EQUATORIAL_RADIUS_METERS,
                                tile_scheme: TileScheme = ZoomTimesTwo(base_matrix_width=1, base_matrix_height=1)):
    """
    Calculates the scale denominator for the zoom level given.

    ________1________    ____meters/pixel_on_device__
    scale_denominator =      meters/pixel on x-axis

    scale_denominator =  ____________________bounds_width_in_meters__________________________
                            (tile_width pixel size)(pixels_per_meter)(number of tiles wide)

    :param zoom_level: the particular zoom level to get the scale value for
    :param tile_size_width: the size of a tile in pixels. If not provided, uses 256 pixel tile.
    :param bounds_meters_width: the real world bounds width in meters. If not provided, uses whole world bounds.
    :param tile_scheme: the tile matrix scheme with the number of tiles per zoom level. If not provided uses default
    one tile at zoom level zero.
    :return: the scale denominator in meters for the particular zoom level
    """
    return bounds_meters_width \
           / (tile_size_width * PIXELS_PER_METER * tile_scheme.get_matrix_dimensions(zoom_level=zoom_level)[0])
