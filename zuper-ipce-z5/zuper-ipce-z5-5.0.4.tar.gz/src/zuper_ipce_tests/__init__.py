from typing import Union

from zuper_typing.annotations_tricks import is_Union

x = Union[int, str]
assert is_Union(x)
