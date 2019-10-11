import re
from typing import *

RegExpType = type(re.compile(r'some_regular'))
JsonSerializable = Union[str, int, float, Dict[str, 'JsonSerializable'], List['JsonSerializable'], None]
Binary = Union[bytes, bytearray, None]

__all__ = \
[
    'RegExpType',
    'JsonSerializable',
    'Binary',
]
