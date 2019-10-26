# -*- coding: utf-8 -*-
# Test some of the pyglow method functions

import numpy as np
import pysat
import pysat.instruments.pysat_testing
from pysatMissionPlanning.methods import pyglow as methglow


def add_altitude(inst, altitude=400.0):
    """Add altitudes to pysat_testing instrument"""

    inst['alt'] = altitude*np.ones()


class TestBasic():
    """Test basic functionality
    """

    def setup(self):
        """Create a clean testing environment"""
        self.inst = pysat.Instrument(platform='pysat', name='testing',
                                     sat_id='100')
        self.inst.custom.add(add_altitude, 'modify')

    def teardown(self):
        """Clean up test environment after tests"""
        del self

    def test_add_iri_thermal_plasma(self):
        """Test adding thermal plasma data to test inst"""
        self.inst.custom.add(methglow.add_iri_thermal_plasma, 'modify',
                             glat_label='latitude', glong_label='longitude',
                             alt_label='alt')
        self.inst.load(date=pysat.datetime(2009, 1, 1))
