# tests.test_stream
# Test the stream utility functions inside of Conduit
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Mon Oct 14 11:20:46 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: test_stream.py [] benjamin@bengfort.com $

"""
Test the stream utility functions inside of Conduit
"""

##########################################################################
## Imports
##########################################################################

import pytest
import numpy as np
import pandas as pd

from conduit.stream import *
from btrdb.utils.timez import ns_delta
from btrdb.point import RawPoint, StatPoint


@pytest.fixture(scope='session')
def raw_points():
    return [
        (RawPoint(time, np.random.rand() * 230000), 39526)
        for time in range(1569414600000000000, 1569414615000000000, 33333000)
    ]


@pytest.fixture(scope='session')
def stat_points():
    def make_stat_point(time):
        vals = np.random.rand(np.random.randint(138, 162)) * 230000
        return StatPoint(
            time, vals.min(), vals.mean(), vals.max(), len(vals), vals.std()
        )

    return [
        (make_stat_point(time), 39526)
        for time in range(1569414600000000000, 1569414720000000000, ns_delta(seconds=5))
    ]


class TestStreamUtilities(object):
    """
    Test stream utility functions inside of Conduit
    """

    def test_points_to_series_values(self, raw_points):
        """
        Test points_to_series from a mock stream.values query result
        """
        series = points_to_series(raw_points, name="test stream")
        assert isinstance(series, pd.Series)
        assert isinstance(series.index, pd.DatetimeIndex)
        assert series.name == "test stream"
        assert series.dtype == np.float64
        assert len(series) == len(raw_points)

    def test_points_to_series_non_datetime64_index(self, raw_points):
        """
        Test points_to_series without a datetime64 index
        """
        series = points_to_series(raw_points, datetime64_index=False)
        assert series.index.dtype == np.int64
        assert len(series) == len(raw_points)
        assert series.name is None

    @pytest.mark.parametrize("agg", ["min", "mean", "max", "count", "stddev"])
    def test_points_to_series_windows(self, agg, stat_points):
        """
        Test points_to_series from a mock stream.windows query result
        """
        name = "test {} stream".format(agg)
        series = points_to_series(stat_points, agg=agg, name=name, dtype=np.float64)

        assert isinstance(series, pd.Series)
        assert isinstance(series.index, pd.DatetimeIndex)
        assert series.name == name
        assert series.dtype == np.float64
        assert len(series) == len(stat_points)

    def test_points_to_series_bad_agg(self, raw_points, stat_points):
        """
        Test exception raised when a bad agg is passed to points_to_series
        """
        # ensure agg is ignored with regular points
        try:
            series = points_to_series(raw_points, agg="foo")
            assert len(series) == len(raw_points)
        except Exception as e:
            pytest.fail("raw points raised exception with bad agg: {}".format(e))

        # test value error when agg is bad with stat points
        with pytest.raises(ValueError, match=r"not a btrdb\.StatPoint aggregate field"):
            points_to_series(stat_points, agg="foo")

    def test_points_to_series_no_version(self, raw_points):
        """
        Test that points_to_series works without versions
        """
        points = [point[0] for point in raw_points]
        series = points_to_series(points)
        assert len(series) == len(raw_points)
