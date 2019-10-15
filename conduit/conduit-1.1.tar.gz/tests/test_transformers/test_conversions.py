# tests.test_transformers.test_conversions
# Test the conversion transformers package
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Sep 17 13:46:29 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: test_conversions.py [] benjamin@bengfort.com $

"""
Test the conversion transformers package
"""

##########################################################################
## Imports
##########################################################################

from conduit.constants import *
from conduit.transformers.conversions import *


class TestConversions(object):

    def test_per_unit_voltage(self, voltage_magnitude):
        """
        Test the per unit conversion of a voltage magnitude
        """
        series, tags, annotations = per_unit(*voltage_magnitude, base_kv=500)
        assert tags[UNIT] == PER_UNIT

    def test_per_unit_current(self, current_magnitude):
        """
        Test the per unit conversion of a current magnitude
        """
        series, tags, annotations = per_unit(*current_magnitude, base_kv=500)
        assert tags[UNIT] == PER_UNIT

    def test_line_to_neutral(self, voltage_magnitude):
        """
        Test the line to neutral conversion of a voltage magnitude
        """
        series, tags, annotations = line_to_neutral(*voltage_magnitude, base_kv=500)
        assert tags[UNIT] == VOLTS_L_N

    def test_line_to_line(self, voltage_magnitude):
        """
        Test the line to line conversion of a voltage magnitude
        """
        series, tags, annotations = line_to_line(*voltage_magnitude, base_kv=500)
        assert tags[UNIT] == VOLTS_L_L

    def test_amps(self, current_magnitude):
        """
        Test converting per-unit values back to amps
        """
        series, tags, annotations = per_unit(*current_magnitude, base_kv=500)
        series, tags, annotations = amps(series, tags, annotations, base_kv=500)
        assert tags[UNIT] == AMPS

    def test_calibrate_voltage_magnitude(self, voltage_magnitude):
        """
        Test calibrate a voltage magnitude
        """
        series, tags, annotations = calibrate(*voltage_magnitude, rcf=32)
        assert annotations[MEASUREMENT_TYPE] == VOLTAGE_MAGNITUDE

    def test_calibrate_voltage_angle(self, voltage_angle):
        """
        Test calibrate a voltage angle
        """
        series, tags, annotations = calibrate(*voltage_angle, pacf=13)
        assert annotations[MEASUREMENT_TYPE] == VOLTAGE_ANGLE
        assert series.min() >= -180.0
        assert series.max() <= 180.0

    def test_calibrate_current_magnitude(self, current_magnitude):
        """
        Test calibrate a current magnitude
        """
        series, tags, annotations = calibrate(*current_magnitude, rcf=32)
        assert annotations[MEASUREMENT_TYPE] == CURRENT_MAGNITUDE

    def test_calibrate_current_angle(self, current_angle):
        """
        Test calibrate a current angle
        """
        series, tags, annotations = calibrate(*current_angle, pacf=13)
        assert annotations[MEASUREMENT_TYPE] == CURRENT_ANGLE
        assert series.min() >= -180.0
        assert series.max() <= 180.0