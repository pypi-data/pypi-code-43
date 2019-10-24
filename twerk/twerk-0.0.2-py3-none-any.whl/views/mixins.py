from abc import ABC, abstractproperty
from datetime import datetime


class ProfileMixin(ABC):
    """Abstract mixin for required Twitter profile properties."""

    @abstractproperty
    def tweets(self) -> int:
        raise NotImplementedError

    @abstractproperty
    def following(self) -> int:
        raise NotImplementedError

    @abstractproperty
    def followers(self) -> int:
        raise NotImplementedError

    @abstractproperty
    def likes(self) -> int:
        raise NotImplementedError

    @abstractproperty
    def joined(self) -> datetime:
        raise NotImplementedError
