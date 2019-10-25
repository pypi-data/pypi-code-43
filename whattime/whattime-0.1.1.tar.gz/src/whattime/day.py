from datetime import datetime
from typing import Set

from .base import InfoBase
from .type import TimeType


class DayTimeInfo(InfoBase):
    __mapping__ = {
        range(0, 4): TimeType.NIGHT,
        range(5, 9): TimeType.MORNING,
        range(10, 11): TimeType.MIDMORNING,
        range(12, 13): TimeType.NOON,
        range(14, 18): TimeType.AFTERNOON,
        range(19, 22): TimeType.EVENING,
        range(23, 24): TimeType.NIGHT
    }

    __inverse_mapping__ = {v: k for k, v in __mapping__.items()}

    @property
    def types(self) -> Set[TimeType]:
        """Return a set of fitting time types for the given datetime"""

        if self._types:
            return self._types

        hour = self.date.hour

        for hours_range, time_type in self.__mapping__.items():
            if hour in hours_range:
                self._types.add(time_type)

        return self._types

    @property
    def is_morning(self) -> bool:
        """Return whether the given datetime is in the morning"""

        return self._is_in_daytime(TimeType.MORNING)

    @property
    def is_midmorning(self) -> bool:
        """Return whether the given datetime is in the midmorning"""

        return self._is_in_daytime(TimeType.MIDMORNING)

    @property
    def is_noon(self) -> bool:
        """Return whether the given datetime is at noon"""

        return self._is_in_daytime(TimeType.NOON)

    @property
    def is_afternoon(self) -> bool:
        """Return whether the given datetime is in the afternoon"""

        return self._is_in_daytime(TimeType.AFTERNOON)

    @property
    def is_evening(self) -> bool:
        """Return whether the given datetime is in the evening"""

        return self._is_in_daytime(TimeType.EVENING)

    @property
    def is_night(self) -> bool:
        """Return whether the given datetime is in the night"""

        return self._is_in_daytime(TimeType.NIGHT)

    def _is_in_daytime(self, time_type: TimeType) -> bool:
        hour_range = self.__inverse_mapping__[time_type]
        return isinstance(hour_range, range) and self.date.hour in hour_range


def day_time_info(date: datetime) -> DayTimeInfo:
    return DayTimeInfo(date)
