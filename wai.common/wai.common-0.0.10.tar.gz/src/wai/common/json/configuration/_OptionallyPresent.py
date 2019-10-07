"""
Defines the OptionallyPresent type, which can take values of
sub-script type T or the singleton Absent value.

E.g. a: OptionallyPresent[int] = |any int or Absent|
"""
from typing import TypeVar, Union

from ._Absent import AbsentType

# The type of the value if it is present
T = TypeVar('T')

OptionallyPresent = Union[AbsentType, T]
