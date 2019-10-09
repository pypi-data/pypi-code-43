"""Unit and regression tests for pupygrib's binary module."""

import io

import pytest
from pytest import approx

from pupygrib import binary


class TestUnpackGrib1FloatFrom:

    """Unit and regression tests for unpack_grib1float_from()."""

    def test_with_max(self):
        max = 7.2370051459731155e75
        assert binary.unpack_grib1float_from(b"\x7f\xff\xff\xff") == approx(max)

    def test_with_plus_one(self):
        assert binary.unpack_grib1float_from(b"\x46\x00\x00\x01") == 1

    def test_with_minus_one(self):
        assert binary.unpack_grib1float_from(b"\xc6\x00\x00\x01") == -1

    def test_with_min(self):
        min = -7.2370051459731155e75
        assert binary.unpack_grib1float_from(b"\xff\xff\xff\xff") == approx(min)

    def test_with_offset(self):
        assert binary.unpack_grib1float_from(b"\xff\x46\x00\x00\x01", 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_grib1float_from(b"\x46\x00\x00")


class TestUnpackInt8From:

    """Unit and regression tests for the unpack_int8_from() function."""

    def test_with_plus_one(self):
        assert binary.unpack_int8_from(b"\x01") == 1

    def test_with_minus_one(self):
        assert binary.unpack_int8_from(b"\x81") == -1

    def test_with_offset(self):
        assert binary.unpack_int8_from(b"\xff\x01", 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_int8_from(b"")


class TestUnpackInt16From:

    """Unit and regression tests for the unpack_int16_from() function."""

    def test_with_plus_one(self):
        assert binary.unpack_int16_from(b"\x00\x01") == 1

    def test_with_minus_one(self):
        assert binary.unpack_int16_from(b"\x80\x01") == -1

    def test_with_offset(self):
        assert binary.unpack_int16_from(b"\xff\x00\x01", 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_int16_from(b"\x01")


class TestUnpackInt24From:

    """Unit and regression tests for the unpack_int24_from() function."""

    def test_with_plus_one(self):
        assert binary.unpack_int24_from(b"\x00\x00\x01") == 1

    def test_with_minus_one(self):
        assert binary.unpack_int24_from(b"\x80\x00\x01") == -1

    def test_with_offset(self):
        assert binary.unpack_int24_from(b"\xff\x00\x00\x01", 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_int24_from(b"\x00\x01")


class TestUnpackUint8From:

    """Unit and regression tests for the unpack_uint8_from() function."""

    def test_with_one(self):
        assert binary.unpack_uint8_from(b"\x01") == 1

    def test_with_max(self):
        assert binary.unpack_uint8_from(b"\xff") == 2 ** 8 - 1

    def test_with_offset(self):
        assert binary.unpack_uint8_from(b"\xff\x01", 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_uint8_from(b"")


class TestUnpackUint16From:

    """Unit and regression tests for the unpack_uint16_from() function."""

    def test_with_one(self):
        assert binary.unpack_uint16_from(b"\x00\x01") == 1

    def test_with_max(self):
        assert binary.unpack_uint16_from(b"\xff\xff") == 2 ** 16 - 1

    def test_with_offset(self):
        assert binary.unpack_uint16_from(b"\xff\x00\x01", 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_uint16_from(b"\x01")


class TestUnpackUint24From:

    """Unit and regression tests for the unpack_uint24_from() function."""

    def test_with_one(self):
        assert binary.unpack_uint24_from(b"\x00\x00\x01") == 1

    def test_with_max(self):
        assert binary.unpack_uint24_from(b"\xff\xff\xff") == 2 ** 24 - 1

    def test_with_offset(self):
        assert binary.unpack_uint24_from(b"\xff\x00\x00\x01", 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_uint24_from(b"\x00\x01")


class TestUnpackUint32From:

    """Unit and regression tests for the unpack_uint32_from() function."""

    def test_with_one(self):
        data = b"\x00\x00\x00\x01"
        assert binary.unpack_uint32_from(data) == 1

    def test_with_max(self):
        data = b"\xff\xff\xff\xff"
        assert binary.unpack_uint32_from(data) == 2 ** 32 - 1

    def test_with_offset(self):
        data = b"\xff\x00\x00\x00\x01"
        assert binary.unpack_uint32_from(data, 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_uint32_from(b"\x00\x00\x01")


class TestUnpackUint64From:

    """Unit and regression tests for the unpack_uint64_from() function."""

    def test_with_one(self):
        data = b"\x00\x00\x00\x00\x00\x00\x00\x01"
        assert binary.unpack_uint64_from(data) == 1

    def test_with_max(self):
        data = b"\xff\xff\xff\xff\xff\xff\xff\xff"
        assert binary.unpack_uint64_from(data) == 2 ** 64 - 1

    def test_with_offset(self):
        data = b"\xff\x00\x00\x00\x00\x00\x00\x00\x01"
        assert binary.unpack_uint64_from(data, 1) == 1

    def test_with_too_few_bytes(self):
        with pytest.raises(binary.error):
            binary.unpack_uint64_from(b"\x00\x00\x00\x00\x00\x00\x01")


class TestCheckread:

    """Unit and regression tests for the checkread() function."""

    def test_read_zero(self):
        assert binary.checkread(io.BytesIO(), 0) == b""

    def test_read_one(self):
        data = b"x"
        assert binary.checkread(io.BytesIO(data), 1) == data

    def test_read_too_much(self):
        with pytest.raises(binary.ParseError) as excinfo:
            binary.checkread(io.BytesIO(), 1)
        assert "unexpected end of file" in str(excinfo.value)
