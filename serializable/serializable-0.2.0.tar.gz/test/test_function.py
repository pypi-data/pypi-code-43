from serializable import (
    to_serializable_repr,
    from_serializable_repr,
)
from nose.tools import eq_

def global_fn():
    pass

def test_serialize_custom_function():
    fn_reconstructed = from_serializable_repr(to_serializable_repr(global_fn))
    eq_(global_fn, fn_reconstructed)


def test_serialize_builtin_function():
    fn_reconstructed = from_serializable_repr(to_serializable_repr(sum))
    eq_(sum, fn_reconstructed)
