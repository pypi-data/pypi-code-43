"""Unit and regression tests for pupygrib's public interface."""

import io
from os import path

import pkg_resources
import pytest

import pupygrib


def open_grib(filename):
    stream = pkg_resources.resource_stream(__name__, path.join("data", filename))
    stream.name = filename
    return stream


class TestRead:

    """Unit and regression tests for the read() function."""

    def test_read_empty_file(self):
        with pytest.raises(StopIteration):
            next(pupygrib.read(io.BytesIO()))

    def test_read_not_a_grib(self):
        with pytest.raises(pupygrib.ParseError) as excinfo:
            next(pupygrib.read(io.BytesIO(b"GRUB")))
        assert "not a GRIB message" in str(excinfo.value)

    def test_read_truncated_header(self):
        with pytest.raises(pupygrib.ParseError) as excinfo:
            next(pupygrib.read(io.BytesIO(b"GRIB")))
        assert "unexpected end of file" in str(excinfo.value)

    def test_read_truncated_edition1_body(self):
        with pytest.raises(pupygrib.ParseError) as excinfo:
            next(pupygrib.read(io.BytesIO(b"GRIB\x00\x00\x09\x01")))
        assert "unexpected end of file" in str(excinfo.value)

    def test_read_truncated_edition2_body(self):
        data = b"GRIBxxx\x02\x00\x00\x00\x00\x00\x00\x00\x11"
        with pytest.raises(pupygrib.ParseError) as excinfo:
            next(pupygrib.read(io.BytesIO(data)))
        assert "unexpected end of file" in str(excinfo.value)

    def test_read_without_end_of_message_marker(self):
        data = b"GRIB\x00\x00\x0c\x017776"
        with pytest.raises(pupygrib.ParseError) as excinfo:
            next(pupygrib.read(io.BytesIO(data)))
        error_message = "end-of-message marker not found"
        assert error_message in str(excinfo.value)

    def test_read_unknown_edition(self):
        with pytest.raises(pupygrib.ParseError) as excinfo:
            next(pupygrib.read(io.BytesIO(b"GRIBxxx\x03")))
        assert "unknown edition number '3'" in str(excinfo.value)

    def test_read_edition1(self):
        with open_grib("regular_latlon_surface.grib1") as stream:
            msg = next(pupygrib.read(stream))
        assert msg.filename.endswith("regular_latlon_surface.grib1")
        assert msg[0].editionNumber == 1

    def test_read_edition2(self):
        with open_grib("regular_latlon_surface.grib2") as stream:
            msg = next(pupygrib.read(stream))
        assert msg.filename.endswith("regular_latlon_surface.grib2")
        assert msg[0].editionNumber == 2
