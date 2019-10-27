from serializable import Serializable
from nose.tools import eq_

class A(Serializable):
    def __init__(self, x, y=1):
        self.x = x
        self.y = y

def test_serializable_default_to_dict():
    a = A(10, 1)
    eq_(a, A.from_dict(a.to_dict()))
