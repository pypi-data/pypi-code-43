#!/usr/bin/env python
# -*- coding: utf-8 -*-

# geoarray, A fast Python interface for image geodata - either on disk or in memory.
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

from unittest import TestCase
import os
import numpy as np
import tempfile

from geoarray.metadata import GDAL_Metadata
from geoarray import GeoArray
import geoarray


tests_path = os.path.abspath(os.path.join(geoarray.__path__[0], "..", "tests"))


class Test_GDAL_Metadata(TestCase):
    @classmethod
    def setUp(cls):
        cls.test_filePath = os.path.join(tests_path, 'data', 'subset_metadata.bsq')
        cls.tmpOutdir = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmpOutdir.cleanup()

    def test_init(self):
        meta = GDAL_Metadata(self.test_filePath)
        self.assertIsInstance(meta, GDAL_Metadata)

    def test_save(self):
        outPath = os.path.join(self.tmpOutdir.name, 'save_bandnames_from_file.bsq')

        gA = GeoArray(self.test_filePath)
        gA.to_mem()
        gA.bandnames = ['test_%s' % i for i in range(1, gA.bands + 1)]
        gA.save(outPath)

        with open(os.path.splitext(outPath)[0] + '.hdr', 'r') as inF:
            content = inF.read()

        for bN in gA.bandnames.keys():
            self.assertTrue(bN in content, msg="The band name '%s' is not in the written header." % bN)

    def test_read_bandnames(self):
        outPath = os.path.join(self.tmpOutdir.name, 'read_bandnames_correctly.bsq')
        bandnames = ['test1', 'band_2', 'layer 3', '12']

        gA = GeoArray(np.random.randint(1, 10, (5, 5, 4)))
        gA.bandnames = bandnames
        gA.save(outPath)

        gA = GeoArray(outPath)
        self.assertEqual(list(gA.bandnames.keys()), bandnames)
        self.assertTrue(all([isinstance(bN, str) for bN in gA.bandnames.keys()]))

    def test_save_bandnames(self):
        outPath = os.path.join(self.tmpOutdir.name, 'save_bandnames_from_numpy.bsq')

        gA = GeoArray(np.random.randint(1, 10, (5, 5, 3)))
        gA.bandnames = ['test1', 'band_2', 'layer 3']
        gA.save(outPath)

        with open(os.path.splitext(outPath)[0] + '.hdr', 'r') as inF:
            content = inF.read()

        for bN in gA.bandnames.keys():
            self.assertTrue(bN in content, msg="The band name '%s' is not in the written header. "
                                               "Header contains:  \n\n%s" % (bN, content))
