from abc import ABC, abstractmethod
from datetime import datetime
from typing import Set

from .type import TimeType


class InfoBase(ABC):
    __mapping__ = {}

    def __init__(self, date: datetime):
        self.date = date
        self._types = set()

    @abstractmethod
    def types(self) -> Set[TimeType]:
        pass
