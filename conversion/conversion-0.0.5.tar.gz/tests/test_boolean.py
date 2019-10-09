import unittest

from nose.tools import assert_equal

from conversion import convert_bool


def test_empty_string():
    """
    Specifically test that an empty string returns False
    """
    assert_equal(False, convert_bool(""))


def test_false():
    """
    Ensure all expected strings return False
    """
    for value in ("no", "n", "false", "f", "0"):
        yield assert_equal, False, convert_bool(value)


def test_true():
    """
    Ensure all expected strings return True
    """
    for value in ("yes", "y", "true", "t", "1"):
        yield assert_equal, True, convert_bool(value)
