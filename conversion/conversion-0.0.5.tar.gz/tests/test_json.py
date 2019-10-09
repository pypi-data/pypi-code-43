import datetime

from json import JSONDecodeError
from nose.tools import assert_equal, assert_raises

from conversion import convert_json


def test_json_dict():
    """
    Ensure json decoding works
    """
    assert_equal({"test": "fool"}, convert_json('{"test": "fool"}'))


def test_json_list():
    """
    Ensure json decoding works
    """
    assert_equal(["test", "fool"], convert_json('["test", "fool"]'))


def test_json_with_error():
    """
    Ensure json error is raised
    """
    assert_raises(JSONDecodeError, convert_json, '["test"')


def test_json_with_error_suppressed():
    """
    Ensure json error is raised
    """
    assert_equal('["test"', convert_json('["test"', raise_exceptions=False))
