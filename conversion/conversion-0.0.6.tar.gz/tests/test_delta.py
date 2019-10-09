import datetime
import unittest

from nose.tools import assert_equal

from conversion import convert_delta


def test_milliseconds():
    """
    Ensure ms suffix is converted to milliseconds
    """
    assert_equal(datetime.timedelta(seconds=0.01), convert_delta("10ms"))


def test_minutes():
    """
    Ensure m suffix is converted to minutes
    """
    assert_equal(datetime.timedelta(minutes=1), convert_delta("1m"))


def test_hours():
    """
    Ensure h suffix is converted to hours
    """
    assert_equal(datetime.timedelta(hours=1), convert_delta("1h"))


def test_days():
    """
    Ensure d suffix is converted to days
    """
    assert_equal(datetime.timedelta(days=1), convert_delta("1d"))


def test_weeks():
    """
    Ensure w suffix is converted to weeks
    """
    assert_equal(datetime.timedelta(days=7), convert_delta("1w"))
