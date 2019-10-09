from collections import Iterable
from typing import Any


def is_iterable(d: Any, exclude_str: bool = True) -> bool:
    """
    refer url: https://docs.python.org/3/glossary.html#term-iterator
    An object capable of returning its members one at a time.
    Examples of iterables include all sequence types (such as list, str, and tuple)
    and some non-sequence types like dict, file objects,
    and objects of any classes you define with an __iter__() method or with a __getitem__() method
    that implements Sequence semantics.
    :param d:
    :return:
    """
    if exclude_str:
        return isinstance(d, Iterable) and not isinstance(d, str)
    else:
        return isinstance(d, Iterable)
