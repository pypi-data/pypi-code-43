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
test_vector
----------_

Tests for `py_tools_ds.numeric.vector` module.
"""

from unittest import TestCase

from py_tools_ds.numeric.vector import find_nearest


class Test_find_nearest(TestCase):
    def setUp(self):
        self.array = [330000.1,
                      330010.19999999995,
                      330020.29999999993,
                      330030.3999999999,
                      330040.4999999999,
                      330050.59999999986,
                      330060.69999999984,
                      330070.7999999998,
                      330080.8999999998,
                      330090.99999999977
                      ]
        self.value = 335442.984382

    def test_round_alg_off(self):
        out = find_nearest(self.array, 330068, roundAlg='off')
        self.assertEqual(out, 330060.69999999984)

    def test_round_alg_on(self):
        out = find_nearest(self.array, 330068, roundAlg='on')
        self.assertEqual(out, 330070.7999999998)

    def test_round_alg_auto(self):
        out = find_nearest(self.array, 330068, roundAlg='auto')
        self.assertEqual(out, 330070.7999999998)

    def test_round_alg_exact_hit(self):
        for roundAlg in ['off', 'on', 'auto']:
            out = find_nearest(self.array, 330060.69999999984, roundAlg=roundAlg)
            self.assertEqual(out, 330060.69999999984)

    def test_extrapolate(self):
        out = find_nearest(self.array, 330110, extrapolate=True, roundAlg='auto')
        self.assertEqual(out, 330111.19999999972)

        out = find_nearest(self.array, 329980, extrapolate=True, roundAlg='auto')
        self.assertEqual(out, 329979.90000000002)

    def test_val_outside(self):
        with self.assertRaises(ValueError):
            find_nearest(self.array, 330110, roundAlg='auto')

    def test_exclude_val(self):
        out = find_nearest(self.array, 330060.69999999984, roundAlg='auto', exclude_val=True)
        self.assertNotEqual(out, 330060.69999999984)

    def test_tolerance(self):
        # value below
        out = find_nearest(self.array, 330060.6999999, roundAlg='off', tolerance=0.0001)
        self.assertEqual(out, 330060.69999999984)  # would return 330050.59999999986 without tolerance

        # value above
        out = find_nearest(self.array, 330060.7, roundAlg='on', tolerance=0.0001)
        self.assertEqual(out, 330060.69999999984)  # would return 330070.7999999998 without tolerance
