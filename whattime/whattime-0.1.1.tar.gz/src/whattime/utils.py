from datetime import datetime
from typing import Set

from .day import DayTimeInfo
from .type import TimeType
from .week import WeekInfo


class TimeInfo(DayTimeInfo, WeekInfo):

    @property
    def types(self) -> Set[TimeType]:
        if not self._types:
            for info_type in TimeInfo.__bases__:
                self._types = self._types.union(info_type(self.date).types)

        return self._types


def whattime(date: datetime) -> TimeInfo:
    return TimeInfo(date)


def week_info(date: datetime) -> WeekInfo:
    return WeekInfo(date)


def day_time_info(date: datetime) -> DayTimeInfo:
    return DayTimeInfo(date)
