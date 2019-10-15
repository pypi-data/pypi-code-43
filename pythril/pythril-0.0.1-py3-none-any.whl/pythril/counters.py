import ast
import builtins
import json

from collections import Counter, Hashable

def serialize_key(key) -> str:
    """Convert a key to its string representation.

    String inputs are assumed to be already properly serialized.
    """
    if not isinstance(key, str):
        key = repr(key)
    return key

def deserialize_key(key: str):
    """Convert a string representation of a key to a simple object."""
    try:
        key = ast.literal_eval(key)
    except ValueError:
        pass
    return key


class ObjectCounter(Counter):
    """A Counter for simple objects such as tuples, dicts, etc.

    Keys are the counted objects.
    """

    def add(self, val):
        """Increment the count for the input value. Each value must be
        hashable.
        """
        self[val] += 1

    def update(self, iterable=None, /, **kwds):
        if iterable is not None and not isinstance(iterable, dict):
            for val in iterable:
                self.add(val)
            iterable = None
        super().update(iterable, **kwds)

    @classmethod
    def from_json(cls, obj: dict, deserializer=None):
        """Deserialize all keys in the input object and return an instance of
        the counter class.

        If a deserialized object is not hashable, it is left in serialized form.
        """
        trans = deserializer or deserialize_key
        counter = cls()
        # dobj = {dk if isinstance(dk, Hashable) else k: v for k, v in
        for key, count in obj.items():
            dkey = trans(key)
            key = dkey if isinstance(dkey , Hashable) else key
            counter[key] = count
        return counter

    def to_json(self, serializer=None) -> dict:
        """Serialize all keys into their string representations."""
        trans = serializer or serialize_key
        return {trans(k): v for k, v in self.items()}


class HashCounter(ObjectCounter):
    """A counter that counts hashed objects.

    Usually the hash function is user-defined, e.g., to generate counts
    utilizing some sort of feature hashing scheme.

    """
    def __init__(self, instance=None, /, hashfunc=None, **kwds):
        self.hash = hashfunc or serialize_key
        super().__init__(instance, **kwds)

    def add(self, val):
        """Increment the count for the input value. It is first hashed."""
        self[self.hash(val)] += 1

    def counts(self, *vals):
        """Return counts for the input values."""
        return ((v, self[self.hash(val)]) for v in vals)


class DictCounter(ObjectCounter):
    """Count the value tuples of dicts.

    The `header` attribute defines which fields to extract when
    the counter is updated.

    For example:
    ```
        counter = DictCounter(header=['x', 'y'])
        counter.add(dict(x=1, y=2, z=3))
        counter[(1,2)] = 1
    ```
    """
    header = None

    def __init__(self, instance=None, /, header=None, **kwds):
        self.header = header or self.header
        super().__init__(instance, **kwds)

    def add(self, val: dict):
        """Update counts for the values tup."""
        keys = self.header or val.keys()
        vals = tuple(val.get(k) for k in keys)
        self[vals] += 1
