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
test_coord_grid
---------------

Tests for `py_tools_ds.geo.coord_grid` module.
"""

import unittest
from shapely.geometry import Polygon

from py_tools_ds.geo.coord_grid import move_shapelyPoly_to_image_grid


poly_local = Polygon([(5708.2, -3006), (5708, -3262), (5452, -3262), (5452, -3006), (5708, -3006)])


class Test_move_shapelyPoly_to_image_grid(unittest.TestCase):

    # TODO test different roundAlgs

    def test_image_coord_grid(self):
        poly_on_grid = move_shapelyPoly_to_image_grid(poly_local, (0, 1, 0, 0, 0, -1), rows=6281, cols=11162)
        self.assertTrue(isinstance(poly_on_grid, Polygon))
        self.assertEqual(str(poly_on_grid), 'POLYGON ((5708 -3262, 5708 -3006, 5452 -3006, 5452 -3262, 5708 -3262))')
