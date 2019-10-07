"""
Time support operations
"""

from __future__ import annotations

from datetime import datetime
from datetime import timezone
from datetime import tzinfo


class Hronos:
    ""

    # discover system time zone
    system_tzinfo:tzinfo = datetime.now().astimezone().tzinfo


class DateTime(datetime):
    "a date/time with time zone always present"

    def __new__(cls,
            year:int, month:int, day:int,
            hour:int=0, minute:int=0, second:int=0, microsecond:int=0,
            tzinfo=Hronos.system_tzinfo,  # use local time zone by default
        ):
        self = super().__new__(cls,
            year, month, day, hour, minute, second, microsecond, tzinfo,
        )
        return self

    @classmethod
    def now(cls, tz=Hronos.system_tzinfo) -> 'DateTime':
        instant = super().now(tz=tz)
        return DateTime(
            year=instant.year,
            month=instant.month,
            day=instant.day,
            hour=instant.hour,
            minute=instant.minute,
            second=instant.second,
            microsecond=instant.microsecond,
            tzinfo=instant.tzinfo,  # local / provided
        )

    @classmethod
    def utcnow(cls):
        instant = super().utcnow()
        return DateTime(
            year=instant.year,
            month=instant.month,
            day=instant.day,
            hour=instant.hour,
            minute=instant.minute,
            second=instant.second,
            microsecond=instant.microsecond,
            tzinfo=timezone.utc,  # utc
        )

    @classmethod
    def strptime(cls, date_string, format:str) -> 'DateTime':
        instant = super().strptime(date_string, format)
        tzinfo = instant.tzinfo or Hronos.system_tzinfo
        return DateTime(
            year=instant.year,
            month=instant.month,
            day=instant.day,
            hour=instant.hour,
            minute=instant.minute,
            second=instant.second,
            microsecond=instant.microsecond,
            tzinfo=tzinfo,  # local / provided
        )

    @classmethod
    def utcfromtimestamp(cls, stamp:float) -> 'DateTime':
        instant = super().utcfromtimestamp(stamp)
        return DateTime(
            year=instant.year,
            month=instant.month,
            day=instant.day,
            hour=instant.hour,
            minute=instant.minute,
            second=instant.second,
            microsecond=instant.microsecond,
            tzinfo=timezone.utc,  # utc
        )

    @property
    def millisecond(self) -> float:
        return self.microsecond / 1000.0

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return self.isoformat()
