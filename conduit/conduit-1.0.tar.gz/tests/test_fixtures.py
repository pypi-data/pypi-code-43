# tests.test_fixtures
# Tests to ensure the BTrDB fixture remains consistent
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Jun 25 16:55:06 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: test_fixtures.py [] benjamin@bengfort.com $

"""
Tests to ensure the BTrDB fixture remains consistent
"""

##########################################################################
## Imports
##########################################################################

import btrdb
import pytest

from .fixtures import FixtureEndpoint


##########################################################################
## Test Fixtures
##########################################################################

class TestFixtures(object):
    """
    Ensure the BTrDB fixture and FixtureEndpoint remain consistent
    """

    def test_info(self, db):
        """
        Test that the db fixture returns info
        """
        info = db.info()
        assert info["build"] == btrdb.__version__
        assert "FixtureEndpoint" in info["proxy"]["proxyEndpoints"]

    def test_get_stream_by_uuid(self, db):
        """
        Should be able to get a stream by uuid
        """
        stream = db.stream_from_uuid("f0fe1f63-864b-4c72-ae58-dc81c67c44ca")
        assert isinstance(stream.btrdb.ep, FixtureEndpoint)
        assert stream.exists()
        assert stream.version() == 1

    def test_list_collections(self, db):
        """
        Should be able to list collections by prefix
        """
        assert len(db.list_collections()) == 1
        assert len(db.list_collections("tst/")) == 1
        assert len(db.list_collections("foo/")) == 0

    def test_streams_in_collection(self, db):
        """
        Should be able to list streams in the collection by prefix
        """
        assert len(db.streams_in_collection("", is_collection_prefix=True)) == 14
        assert len(db.streams_in_collection("tst/", is_collection_prefix=True)) == 14
        assert len(db.streams_in_collection("tst/", is_collection_prefix=False)) == 0
        assert len(db.streams_in_collection("foo/", is_collection_prefix=True)) == 0

        streams = db.streams_in_collection("tst/TST!PMU-DCA1_732", is_collection_prefix=True)
        assert len(streams) == 14

        for stream in streams:
            assert isinstance(stream.btrdb.ep, FixtureEndpoint)

    def test_streams_in_collection_by_tags(self, db):
        """
        Should be able to list streams in collection filtering by tag
        """
        streams = db.streams_in_collection("", tags={"unit": "VPHM"})
        assert len(streams) == 3

        for stream in streams:
            assert stream.tags()["unit"] == "VPHM"

    def test_streams_in_collection_by_annotations(self, db):
        """
        Should be able to list streams in collection filtering by annotation
        """
        streams = db.streams_in_collection("", annotations={"phase": "A"})
        assert len(streams) == 4

        for stream in streams:
            meta, _ = stream.annotations()
            assert meta["phase"] == "A"

    def test_streams_nearest_latest_earliest(self, db):
        """
        Should be able to get the earliest and latest timestamps from a stream
        """
        stream = db.stream_from_uuid("f0fe1f63-864b-4c72-ae58-dc81c67c44ca")

        ept, v = stream.earliest()
        assert v == 1
        assert ept.time == 1560513600000000000
        assert ept.value == pytest.approx(269.732727)

        lpt, v = stream.latest()
        assert v == 1
        assert lpt.time == 1560517199999999800
        assert lpt.value == pytest.approx(304.390259)

    def test_stream_values(self, db):
        """
        Should be able to get a subset of values from the dataset
        """
        stream = db.stream_from_uuid("f0fe1f63-864b-4c72-ae58-dc81c67c44ca")
        values = stream.values(start='2019-06-14 12:00:00.000000', end='2019-06-14 12:00:00.966666')
        assert len(values) == 29

    def test_get_stream_set(self, db):
        """
        Test that a StreamSet is returned from the db.streams query
        """
        streams = db.streams(
            "2713d533-6538-49b9-894d-0ab80150653d",
            "0e044521-acb7-4121-9be9-3258095611fe",
            "639cdd2b-5e19-44ba-9550-47017e8a459c",
        )

        start = min([point.time for point in streams.earliest()])
        end = max([point.time for point in streams.latest()])
        streams = streams.filter(start=start, end=end)

        df = streams.to_dataframe()
        assert df.shape == (107870, 3)