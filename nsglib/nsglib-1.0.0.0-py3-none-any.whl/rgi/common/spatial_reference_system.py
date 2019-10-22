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
from enum import Enum

from nsg.rgi.common.bounding_box import BoundingBox
from nsg.rgi.tile_cache.tile_scheme import TileScheme, ZoomTimesTwo

EARTH_EQUATORIAL_RADIUS_METERS = 6378137.0


class SpatialReferenceSystem(Enum):
    """Spatial Reference System constants."""

    def __init__(self,
                 srs_name: str,
                 coordinate_reference_system_code: int,
                 coordinate_reference_system_organization: str,
                 well_known_text: str,
                 world_bounding_box: BoundingBox,
                 tile_scheme: TileScheme):
        """
        Initialize the Spatial Reference System Enum.
        :param tile_scheme: Mechanism to describe the number of tiles in a tile set, at a given zoom level
        :param srs_name: name of the spatial reference system . (i.e. WGS 84 Geographic 2D)
        :type srs_name: str
        :param coordinate_reference_system_code: the projection code as a float (i.e. 4326)
        :type coordinate_reference_system_code: float
        :param coordinate_reference_system_organization: organization name(i.e. 'EPSG')
        :type coordinate_reference_system_organization: str
        :param well_known_text: well known text for the srs
        :type well_known_text: str
        :param world_bounding_box: the bounds of the spatial reference system
        :type world_bounding_box: BoundingBox
        """
        self.srs_name = srs_name
        self.coordinate_reference_system_code = coordinate_reference_system_code
        self.coordinate_reference_system_organization = coordinate_reference_system_organization
        self.well_known_text = well_known_text
        self.world_bounding_box = world_bounding_box
        self.tile_scheme = tile_scheme

    def __new__(cls, *args, **kwds):  # pylint: disable=W0613
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value  # pylint: disable=W0212
        return obj

    NSG_WORLD_GEODETIC = "WGS 84 Geographic 2D", \
                         4326, \
                         'EPSG', \
                         """
                            GEOGCS["WGS 84",
                            DATUM["WGS_1984",
                            SPHEROID["WGS84",6378137,298.257223563,]],
                            PRIMEM["Greenwich",0],
                            UNIT["degree",0.0174532925199433]]
                         """, \
                         BoundingBox(min_x=-180.0, max_x=180.0, min_y=-90.0, max_y=90.0), \
                         ZoomTimesTwo(base_matrix_height=1,
                                      base_matrix_width=2)

    WEB_MERCATOR = 'WGS 84 / Pseudo-Mercator', \
                   3857, \
                   'EPSG', \
                   """
                      PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984"
                      ,SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]]
                      ,AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG",
                      "8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]
                      ,AUTHORITY["EPSG","9122"]]AUTHORITY["EPSG","4326"]],PROJECTION[
                      "Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER[
                      "scale_factor",1],PARAMETER["false_easting",0],PARAMETER[
                      "false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS[
                      "X",EAST],AXIS["Y",NORTH]
                   """, \
                   BoundingBox(min_x=-math.pi * EARTH_EQUATORIAL_RADIUS_METERS,
                               max_x=math.pi * EARTH_EQUATORIAL_RADIUS_METERS,
                               min_y=-math.pi * EARTH_EQUATORIAL_RADIUS_METERS,
                               max_y=math.pi * EARTH_EQUATORIAL_RADIUS_METERS), \
                   ZoomTimesTwo(base_matrix_height=1,
                                base_matrix_width=1)

    NSG_WORLD_MERCATOR = "WGS 84 / World Mercator", \
                         3395, \
                         'EPSG', \
                         """PROJCRS["WGS 84 / World Mercator",
                        BASEGEODCRS["WGS 84",
                            DATUM["World Geodetic System 1984",
                                 ELLIPSOID["WGS 84",6378137,298.257223563,]]],
                        CONVERSION["Mercator",
                            METHOD["Mercator (variant A)",ID["EPSG","9804"]],
                            PARAMETER["Latitude of natural origin",0,
                                ANGLEUNIT["degree",0.0174532925199433]],
                            PARAMETER["Longitude of natural origin",0,
                                ANGLEUNIT["degree",0.0174532925199433]],
                            PARAMETER["Scale factor at natural origin",1,
                                SCALEUNIT["unity",1.0]],
                            PARAMETER["False easting",0,LENGTHUNIT["metre",1.0]],
                            PARAMETER["False northing",0,LENGTHUNIT["metre",1.0]],
                            ID["EPSG","19833"]],
                        CS[Cartesian,2],
                            AXIS["Easting (E)",east,ORDER[1]],
                            AXIS["Northing (N)",north,ORDER[2]],
                            LENGTHUNIT["metre",1.0]
                        ID["EPSG","3395"]]""", \
                         BoundingBox(min_x=-math.pi * EARTH_EQUATORIAL_RADIUS_METERS,
                                     max_x=math.pi * EARTH_EQUATORIAL_RADIUS_METERS,
                                     min_y=-math.pi * EARTH_EQUATORIAL_RADIUS_METERS,
                                     max_y=math.pi * EARTH_EQUATORIAL_RADIUS_METERS), \
                         ZoomTimesTwo(base_matrix_height=1,
                                      base_matrix_width=1)

    UNDEFINED_CARTESIAN_CRS = 'undefined cartesian coordinate reference system', \
                              -1, \
                              'NONE', \
                              'undefined', \
                              None,\
                              None

    UNDEFINED_GEOGRAPHIC_CRS = 'undefined geographic coordinate reference system', \
                               0, \
                               'NONE', \
                               'undefined', \
                               None, \
                               None

    @staticmethod
    def get_srs_from_code(code):
        """
        Returns the SpatialReferenceSystem enum based on the epsg code given.
        :param code: the epsg code of the spatial reference system to get.
        :type code: int
        :return: the SpatialReferenceSystem enum based on the epsg code given.
        :rtype: SpatialReferenceSystem
        """
        srs = next(iter(srs for srs in SpatialReferenceSystem if srs.coordinate_reference_system_code == code), None)
        if srs is None:
            raise ValueError("No support for the spatial reference system with code {code}".format(code=code))
        return srs
