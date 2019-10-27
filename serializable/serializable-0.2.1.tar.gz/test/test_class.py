from serializable import (
    from_serializable_repr,
    to_serializable_repr
)
from nose.tools import eq_

class A(object):
    pass

def test_serialize_custom_class():
    A_reconstructed = from_serializable_repr(to_serializable_repr(A))
    eq_(A, A_reconstructed)


def test_serialize_builtin_class():
    int_reconstructed = from_serializable_repr(to_serializable_repr(int))
    eq_(int, int_reconstructed)
