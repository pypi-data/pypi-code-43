import base64
import binascii

from nose.tools import assert_equal, assert_raises

from conversion import convert_base64


def test_basic():
    """
    Ensure basic decoding works
    """
    assert_equal("test", convert_base64(base64.b64encode(b"test")))


def test_bytes():
    """
    Ensure string conversion kwarg works
    """
    assert_equal(
        b"test", convert_base64(base64.b64encode(b"test"), convert_string=False)
    )


def test_exception():
    """
    Ensure bad b64 string returns the original string
    """
    assert_equal("notb64test", convert_base64("notb64test"))


def test_exception_raised():
    """
    Ensure raise_exceptions kwarg works
    """
    assert_raises(binascii.Error, convert_base64, "notb64test", raise_exceptions=True)
