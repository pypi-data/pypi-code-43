from serializable import (
    from_serializable_repr,
    to_serializable_repr
)
from nose.tools import eq_

def test_int():
    eq_(1, from_serializable_repr(to_serializable_repr(1)))

def test_float():
    eq_(1.4, from_serializable_repr(to_serializable_repr(1.4)))

def test_bool():
    eq_(False, from_serializable_repr(to_serializable_repr(False)))

def test_str():
    eq_("waffles", from_serializable_repr(to_serializable_repr("waffles")))
