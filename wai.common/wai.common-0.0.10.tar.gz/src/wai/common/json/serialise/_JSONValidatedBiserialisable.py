from abc import ABC

from ..validator import JSONValidatorClass
from ._JSONBiserialisable import JSONBiserialisable, T


class JSONValidatedBiserialisable(JSONValidatorClass, JSONBiserialisable[T], ABC):
    """
    Utility interface that specifies that a class is both biserialisable
    with JSON and that that JSON is validated.
    """
    pass
