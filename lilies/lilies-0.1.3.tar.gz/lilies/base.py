from builtins import object
from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass


class LilyBase(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def wilt(self):
        raise NotImplementedError("wilt")

    @abstractmethod
    def _isstringish(self):
        raise NotImplementedError("_isstringish")

    @abstractmethod
    def _isblockish(self):
        raise NotImplementedError("_isblockish")

    @classmethod
    def __subclasshook__(cls, subclass):
        required = ["wilt", "_isstringish", "_isblockish"]
        for r in required:
            if not any(r in c.__dict__ for c in subclass.__mro__):
                return NotImplemented
        return True
