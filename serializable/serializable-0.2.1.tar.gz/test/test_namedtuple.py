from collections import namedtuple
from serializable import to_serializable_repr, from_serializable_repr
from nose.tools import eq_

A = namedtuple("A", "x y")

instance = A(1, 2)

def test_namedtuple_to_json():
    eq_(instance, from_serializable_repr(to_serializable_repr(instance)))
