from datetime import datetime
from typing import Set

from .base import InfoBase
from .type import TimeType


class WeekInfo(InfoBase):
    __mapping__ = {
        'is_weekend': TimeType.WEEKEND,
        'is_weekday': TimeType.WEEKDAY,
        'is_monday': TimeType.MONDAY,
        'is_tuesday': TimeType.TUESDAY,
        'is_wednesday': TimeType.WEDNESDAY,
        'is_thursday': TimeType.THURSDAY,
        'is_friday': TimeType.FRIDAY,
        'is_saturday': TimeType.SATURDAY,
        'is_sunday': TimeType.SUNDAY
    }

    @property
    def types(self) -> Set[TimeType]:
        """Return a set of fitting time types for the given datetime"""

        if self._types:
            return self._types

        for prop, time_type in self.__mapping__.items():
            predicate = self.__getattribute__(prop)

            if predicate:
                self._types.add(time_type)

        return self._types

    @property
    def is_weekend(self) -> bool:
        """Return whether the given datetime is a weekend day"""

        return self.is_saturday or self.is_sunday

    @property
    def is_weekday(self) -> bool:
        """Return whether the given datetime is a weekday"""

        return not self.is_weekend

    @property
    def is_monday(self) -> bool:
        """Return whether the given datetime is a Monday"""

        return self.date.isoweekday() == 1

    @property
    def is_tuesday(self) -> bool:
        """Return whether the given datetime is a Tuesday"""

        return self.date.isoweekday() == 2

    @property
    def is_wednesday(self) -> bool:
        """Return whether the given datetime is a Monday"""

        return self.date.isoweekday() == 3

    @property
    def is_thursday(self) -> bool:
        """Return whether the given datetime is a Thursday"""
        return self.date.isoweekday() == 4

    @property
    def is_friday(self) -> bool:
        """Return whether the given datetime is a Friday"""

        return self.date.isoweekday() == 5

    @property
    def is_saturday(self) -> bool:
        """Return whether the given datetime is a Saturday"""

        return self.date.isoweekday() == 6

    @property
    def is_sunday(self) -> bool:
        """Return whether the given datetime is a Sunday"""

        return self.date.isoweekday() == 7


def week_info(date: datetime) -> WeekInfo:
    return WeekInfo(date)
