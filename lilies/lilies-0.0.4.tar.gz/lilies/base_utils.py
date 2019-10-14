from builtins import str
from future.utils import string_types
from .base import LilyBase


def wilt(s):
    if isinstance(s, LilyBase):
        return s.wilt()
    else:
        return str(s)


def isstringish(obj):
    if issubclass(type(obj), LilyBase):
        # This is a hack, since for whatever reason
        # python considers LilyBase and LilyString to
        # both be instances of one another.
        return obj._isstringish()
    return isinstance(obj, (string_types,))


def assert_stringish(obj):
    if not isstringish(obj):
        raise TypeError("Expected something string-like: " + repr(obj))


def islilyblock(obj):
    return isinstance(obj, LilyBase) and obj._isblockish()


def assert_lilyblock(obj):
    if not islilyblock(obj):
        raise TypeError("Expected LilyBlock: " + repr(obj))
