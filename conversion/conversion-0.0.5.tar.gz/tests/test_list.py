import datetime

from nose.tools import assert_equal

from conversion import convert_list


def test_delimeter():
    """
    Ensure the delimeter kwarg is used
    """
    assert_equal(["a", "b"], convert_list("a:b", delimeter=":"))


def test_single_element():
    """
    Ensure a string without a delimeter is returned as a single element list
    """
    assert_equal(["a"], convert_list("a"))


def test_split_and_stripped():
    """
    Ensure spaces are stripped off values
    """
    assert_equal(["a", "b"], convert_list("a, b"))
