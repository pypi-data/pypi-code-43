"""Unit tests for reading grib files with zero-padded messages."""

from pkg_resources import resource_stream

import pupygrib


def test_read_zeropadded_messages():
    with resource_stream(__name__, "data/zeropadded.grib") as stream:
        messages = list(pupygrib.read(stream))
    assert len(messages) == 3
