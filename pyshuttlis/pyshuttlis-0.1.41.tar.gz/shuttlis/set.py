# Adding this directly here as I was unable to find a package for this.
# from http://code.activestate.com/recipes/576932-sets-with-a-custom-equalityuniqueness-function/
"""
FrozenKeyedSet and KeyedSet are set implementations that use
a custom element equality function, so that set membership and
uniqueness is not based on the element's __eq__ but on a user-supplied
function.

>>> class Foo(object):
...   def __init__(self, name): self.name = name
...   def __repr__(self): return "%s(%r)" % (type(self).__name__, self.name)
>>> def getname(o):
...   return o.name
>>> objs = [Foo('Joe'), Foo('Jim'), Foo('Tom'), Foo('Jim')]
>>> s = KeyedSet(objs, key=getname)
>>> s
KeyedSet([Foo('Jim'), Foo('Joe'), Foo('Tom')])
>>> s.add(Foo('Joe'))
>>> len(s)
3
>>> joe = Foo('Joe')
>>> joe in s
True
>>> 'Joe' in s
False
>>> s2 = set([Foo('Luc'), Foo('Jim'), Foo('Dan')])
>>> s | s2
KeyedSet([Foo('Dan'), Foo('Jim'), Foo('Luc'), Foo('Joe'), Foo('Tom')])
>>> s & s2
KeyedSet([Foo('Jim')])
>>> s2f = FrozenKeyedSet(s2, key=getname)
>>> s2f - s
FrozenKeyedSet([Foo('Dan'), Foo('Luc')])
>>> for elem in s ^ s2f:
...   print(elem.name)
Dan
Luc
Joe
Tom
>>> s.copy()
KeyedSet([Foo('Jim'), Foo('Joe'), Foo('Tom')])
>>> # FrozenKeyedSet can be used as dictionary key
... d = {}
>>> d[s2f] = ['anything', 'else']

Copyright (C) 2009 Gabriel A. Genellina

"""

__author__ = "Gabriel A. Genellina"
__version__ = "$Revision: 1.12 $"[11:-2]

from collections.abc import Set, MutableSet


# Abstract classes Set and MutableSet define only the operators (&, &=, etc.)
# but not the corresponding "worded" methods (intersection, intersection_update, etc.)
# The former require a Set second argument, the later accept any iterable.
# This helper function is used to build the "worded" method variant on top of
# the corresponding operator.
def _build_variant(cls, opname):
    fn = getattr(cls, opname)
    if hasattr(fn, "im_func"):
        fn = fn.im_func

    def method(self, other, fn=fn):
        if not isinstance(other, Set):
            other = self._from_iterable(other)
        return fn(self, other)

    return method


class FrozenKeyedSet(Set):
    """A frozen set that uses a custom element equality function."""

    # "named" methods like those of frozenset, in addition to operators
    intersection = _build_variant(Set, "__and__")
    union = _build_variant(Set, "__or__")
    difference = _build_variant(Set, "__sub__")
    symmetric_difference = _build_variant(Set, "__xor__")
    issubset = _build_variant(Set, "__le__")
    issuperset = _build_variant(Set, "__ge__")

    def __init__(self, iterable, key=lambda x: x):
        """Create a FrozenKeyedSet from iterable; key function determines uniqueness.

        `key` must be a callable taking a single argument; it is
        applied to every item in the iterable, and its result
        is used to determine set membership. That is, if key(item)
        returns the same for two items, only one of them will be
        in the set.
        The key *must* return a hashable object.
        """
        self._items = dict((key(item), item) for item in iterable)
        self._key = key

    # Implementation of abstract methods from the Set ABC

    def __iter__(self):
        return iter(self._items.values())

    def __contains__(self, value):
        try:
            key = self._key(value)
        except Exception:
            return False
        return key in self._items

    def __len__(self):
        return len(self._items)

    # NOT a classmethod because self.key must be transferred too!
    # Fortunately it is always called as self._from_iterable(...)
    # in _abccoll.py
    def _from_iterable(self, iterable):
        return type(self)(iterable, key=self._key)

    def copy(self):
        return type(self)(self._items.values(), key=self._key)

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, list(self._items.values()))

    def __hash__(self):
        # Set already provides an implementation for a hash method (_hash),
        # but we have to apply it to the keys only.
        # Python 2.x requires the 'self' argument to be a Set instance,
        # so we call the underlying function directly. Python 3.x has
        # relaxed the requirement.
        _hash = Set._hash
        if hasattr(_hash, "im_func"):
            _hash = _hash.im_func
        return _hash(self._items.keys())


class KeyedSet(FrozenKeyedSet, MutableSet):
    """A mutable set that uses a custom element equality function."""

    # "named" methods like those of `set` class, in addition to operators
    intersection_update = _build_variant(MutableSet, "__iand__")
    update = _build_variant(MutableSet, "__ior__")
    difference_update = _build_variant(MutableSet, "__isub__")
    symmetric_difference_update = _build_variant(MutableSet, "__ixor__")

    __hash__ = None  # because FrozenKeyedSet implements it

    # Implementation of abstract methods from the MutableSet ABC

    def add(self, value):
        """Add an element."""
        key = self._key(value)
        if key not in self._items:
            self._items[key] = value

    def discard(self, value):
        """Remove an element.  Do not raise an exception if absent."""
        key = self._key(value)
        try:
            del self._items[key]
        except KeyError:
            pass

    # performance: override implementation in MutableSet
    def clear(self):
        self._items.clear()
