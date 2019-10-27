from serializable import (
    to_serializable_repr,
    from_serializable_repr,
    to_json,
    from_json,
)
from nose.tools import eq_

def test_tuple_to_serializable():
    x = {1, 2.0, "wolves"}
    eq_(x, from_serializable_repr(to_serializable_repr(x)))

def test_tuple_to_json():
    x = {1, 2.0, "wolves"}
    eq_(x, from_json(to_json(x)))
