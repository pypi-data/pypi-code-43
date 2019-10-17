#!/usr/bin/env python
# -*- coding: utf-8 -*-

# py_tools_ds
#
# Copyright (C) 2019  Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz-potsdam.de)
#
# This software was developed within the context of the GeoMultiSens project funded
# by the German Federal Ministry of Education and Research
# (project grant code: 01 IS 14 010 A-C).
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
test_projection
----------------------------------

Tests for `py_tools_ds.geo.projection` module.
"""


import unittest

from py_tools_ds.geo.projection import WKT2EPSG, EPSG2WKT

wkt_utm = \
    """
    PROJCS["WGS 84 / UTM zone 33N",
           GEOGCS["WGS 84",
                  DATUM["WGS_1984",
                        SPHEROID["WGS 84", 6378137, 298.257223563,
                                 AUTHORITY["EPSG", "7030"]],
                        AUTHORITY["EPSG", "6326"]],
                  PRIMEM["Greenwich", 0,
                         AUTHORITY["EPSG", "8901"]],
                  UNIT["degree", 0.0174532925199433,
                       AUTHORITY["EPSG", "9122"]],
                  AUTHORITY["EPSG", "4326"]],
           PROJECTION["Transverse_Mercator"],
           PARAMETER["latitude_of_origin", 0],
           PARAMETER["central_meridian", 15],
           PARAMETER["scale_factor", 0.9996],
           PARAMETER["false_easting", 500000],
           PARAMETER["false_northing", 0],
           UNIT["metre", 1,
                AUTHORITY["EPSG", "9001"]],
           AXIS["Easting", EAST],
           AXIS["Northing", NORTH],
           AUTHORITY["EPSG", "32633"]]
    """


class Test_WKT2EPSG(unittest.TestCase):

    def setUp(self):
        self.wkt_utm = wkt_utm

    def test_UTM_wkt(self):
        epsg = WKT2EPSG(self.wkt_utm, epsgfile='')
        self.assertTrue(isinstance(epsg, int))


class Test_EPSG2WKT(unittest.TestCase):

    def setUp(self):
        self.epsg_utm = 32636

    def test_UTM_epsg(self):
        wkt = EPSG2WKT(self.epsg_utm)
        self.assertTrue(isinstance(wkt, str), "EPSG2WKT returned a %s object instead of a string!" % type(wkt))
        self.assertNotEquals(wkt, "", msg="EPSG2WKT returned an empty WKT string!")
