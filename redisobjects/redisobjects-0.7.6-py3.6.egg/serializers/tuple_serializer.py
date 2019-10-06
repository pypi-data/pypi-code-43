from .identity_serializer import IdentitySerializer

class TupleSerializer:
    def __init__(self, *value_serializers, separator=','):
        self.value_serializers = value_serializers
        self.separator = separator

    def serialize(self, value):
        if type(value) is not tuple:
            raise RuntimeError("Value must be a tuple!")
        if len(value) != len(self.value_serializers):
            raise RuntimeError("Tuple must be of size %s" % (len(self.value_serializers),))
        return self.separator.join((self.value_serializers[i].serialize(value[i]) for i in range(len(value))))

    def deserialize(self, value):
        parts = value.decode().split(self.separator)
        n = len(self.value_serializers)
        if len(parts) != n:
            raise RuntimeError("Tuple must be of size %s" % (n,))
        return tuple((self.value_serializers[i].deserialize(parts[i]) for i in range(n)))

    '''
    Create a homogeneous TupleSerializer. In other words, lift some serializer f for some type T to
    n-tuples of type T^n, apply the string join function for some separator s, and call the new function g.
    Then g(x_1, x_2, ..., x_n) = s.join(f(x_1), f(x_2), ..., f(x_n)).
    '''
    @staticmethod
    def create_homogeneous(n, value_serializer=IdentitySerializer(), *, separator=','):
        value_serializers = [value_serializer] * n
        return TupleSerializer(*value_serializers, separator=separator)
