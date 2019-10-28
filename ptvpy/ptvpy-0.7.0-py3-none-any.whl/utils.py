"""Utility tools like data containers and other helpers.

Generally speaking, if a helper functions or class is self-contained and is not
really specific to a more specialized module it is a good candidate for
inclusion here. To make using these helpers easy and cheap this module should
have a low import cost and thus shouldn't use expensive external frameworks.
"""


import warnings
import pprint
import re
from collections.abc import Sequence, Mapping
from functools import lru_cache
from contextlib import contextmanager


__all__ = ["LazyMapSequence", "ChainedKeyMap", "expected_warning", "natural_sort_key"]


class LazyMapSequence(Sequence):
    """A sequence that applies a function to its items only when accessed.

    Parameters
    ----------
    function : callable
        The function to apply to `items`.
    items : iterable
        An iterable that returns one input argument for `function`.
    cache_size : int, optional
        If a value larger 0 is given, the results of `function` are cached with
        a last recently used cache (LRU) cache of this size.

    Examples
    --------

    >>> files = ["a.txt", "b.txt", "c.txt", "d.txt"]  # doctest: +SKIP
    >>> for file in files:  # doctest: +SKIP
    ...     with open(file, "x") as stream:
    ...         stream.write(f"Content of {file}")
    >>> def load(file):
    ...     print(f"Loading {file}")
    ...     with open(file) as stream:
    ...         return stream.read()
    >>> sequence = LazyMapSequence(load, files, cache_size=2)  # doctest: +SKIP
    >>> len(sequence)  # doctest: +SKIP
    4
    >>> len(sequence[1:])  # doctest: +SKIP
    3
    >>> sequence[3]  # doctest: +SKIP
    Loading c.txt
    >>> sequence[3]  # doctest: +SKIP
    """

    def __init__(self, function, items, cache_size=0):
        self.function = function  #: Same as constructor parameter.
        self.items = tuple(items)  #: Same as constructor parameter.

        self._cache_size = cache_size
        if self._cache_size > 0:
            self._get_item = lru_cache(self._cache_size)(self._get_item)

    @property
    def cache_size(self):
        """The size of the LRU cache (int, readonly)."""
        return self._cache_size

    def clear_cache(self):
        """Clear the cache.

        Does nothing if :attr:`~.cache_size` is 0.
        """
        try:
            self._get_item.cache_clear()
        except AttributeError:
            pass

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i_or_slice):
        if isinstance(i_or_slice, slice):
            return self._sliced_subset(i_or_slice)
        else:
            return self._get_item(i_or_slice)

    def _sliced_subset(self, sl):
        # Return new sliced LazyLoadingSequence
        return LazyMapSequence(self.function, self.items[sl], self._cache_size)

    def _get_item(self, i):
        item = self.function(self.items[i])
        return item


class ChainedKeyMap(Mapping):
    """Immutable mapping that implements fancier indexing.

    Parameters
    ----------
    mapping : Mapping
        A mapping to create this class from.
    delimiter : str, optional
        If keys are given as a string this character (sequence) is used to
        split the chained keys.

    Examples
    --------
    >>> ckm = ChainedKeyMap({"a": {"b": 1}, "c": [2, 3, {"d": 4}]})
    >>> ckm["a.b"]
    1
    >>> ckm[("c", 2, "d")]
    4
    >>> ckm[["a.b", ("c", 0)]]
    (1, 2)
    """

    def __init__(self, mapping, delimiter="."):
        self._dict = dict(mapping)
        self.delimiter = delimiter  #: Same as constructor parameter.

    def __getitem__(self, keys):
        if isinstance(keys, list):
            return tuple(self[k] for k in keys)
        return self._get_item(keys)

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return self._dict.__iter__()

    def __repr__(self):
        cls_name = type(self).__name__
        return f"{cls_name}(\n{str(self)},\ndelimiter='{self.delimiter}')"

    def __str__(self):
        return pprint.pformat(self._dict)

    def _get_item(self, keys):
        if isinstance(keys, str):
            keys = keys.split(self.delimiter)
        value = self._dict
        try:
            for key in keys:
                value = value[key]
        except (TypeError, KeyError) as e:
            # Turn Errors into KeyError so that methods of the base class
            # can catch this exception
            raise KeyError(*e.args)
        if isinstance(value, Mapping):
            value = ChainedKeyMap(value, self.delimiter)
        return value


@contextmanager
def expected_warning(message="", category=Warning, module=""):
    """Catch and ignore expected warning.

    Parameters
    ----------
    message : str
        A string compiled to a regular expression that is matched against
        raised warnings to decide whether they are expected.
    category : builtin warning
        A warning category.
    module : str
        A string compiled to a regular expression that is matched against
        the module name of raised warnings to decide whether they are expected.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message, category, module)
        yield


def natural_sort_key(item):
    """Transforms strings into tuples that can be sorted in natural order [1]_.

    This can be passed to the "key" argument of Python's `sorted` function.

    Parameters
    ----------
    item :
        Item to generate the key from. `str` is called on this item before generating
        the key.

    Returns
    -------
    key : tuple[str or int]
        Key to sort by.

    Examples
    --------
    >>> from ptvpy.utils import natural_sort_key
    >>> natural_sort_key("image_2.png")
    ('image_', 2, '.png')
    >>> natural_sort_key("image_10.png")
    ('image_', 10, '.png')
    >>> sorted(["10.b", "2.c", "100.a"], key=natural_sort_key)
    ['2.c', '10.b', '100.a']

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Natural_sort_order
    """
    splitted = re.split(r"(\d+)", str(item))
    return tuple(int(x) if x.isdigit() else x for x in splitted)
