from serializable import (
    from_serializable_repr,
    to_serializable_repr,
    Serializable,
)
from nose.tools import eq_
import pickle

class A(Serializable):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_dict(self):
        return {"x": self.x, "y": self.y}

instance = A(1, 2)

def test_serialize_object_with_helpers():
    instance_reconstructed = from_serializable_repr(
        to_serializable_repr(instance))
    eq_(instance, instance_reconstructed)

def test_object_to_json():
    eq_(instance, A.from_json(instance.to_json()))

def test_object_pickle():
    eq_(instance, pickle.loads(pickle.dumps(instance)))
