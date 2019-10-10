from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Optional, Generator

import pytz


def time_now() -> datetime:
    return pytz.utc.localize(datetime.utcnow())


def from_iso_format(d: str, tz=pytz.utc) -> datetime:
    return datetime.fromisoformat(d).astimezone(tz)


def maybe_datetime_from_iso_format(d: str, tz=pytz.utc) -> Optional[datetime]:
    return datetime.fromisoformat(d).astimezone(tz) if d else None


def date_from_iso_format(d: str, tz=pytz.utc) -> date:
    time = datetime.fromisoformat(d).astimezone(tz) + timedelta(hours=12)
    return time.date()


def maybe_date_from_iso_format(d: str, tz=pytz.utc) -> Optional[date]:
    time = datetime.fromisoformat(d).astimezone(tz) + timedelta(hours=12) if d else None
    return time.date() if time else None


@dataclass(frozen=True)
class TimeDeltaWindow:
    lower: Optional[timedelta]
    upper: Optional[timedelta]

    @classmethod
    def from_minutes(cls, lower: int, upper: int):
        lower = timedelta(minutes=lower)
        upper = timedelta(minutes=upper)
        return cls(lower, upper)

    @classmethod
    def from_days(cls, lower: int, upper: int):
        lower = timedelta(days=lower)
        upper = timedelta(days=upper)
        return cls(lower, upper)


class TimeWindowError(Exception):
    pass


@dataclass
class TimeWindow:
    def __init__(self, from_date: datetime = None, to_date: datetime = None):
        from_date = from_date or pytz.utc.localize(datetime.min)
        to_date = to_date or pytz.utc.localize(datetime.max)

        assert to_date > from_date

        self.__from_date = from_date
        self.__to_date = to_date

    @property
    def from_date(self):
        return self.__from_date

    @property
    def to_date(self):
        return self.__to_date

    def __contains__(self, item):
        return self.from_date <= item <= self.to_date

    def __str__(self):
        return f"{self.from_date.isoformat()} - {self.to_date.isoformat()}"

    def __hash__(self):
        return hash((self.from_date, self.to_date))

    def intersects(self, other: "TimeWindow"):
        return other.from_date in self or other.to_date in self

    def intersection(self, other: "TimeWindow"):
        if not self.intersects(other):
            raise ValueError("No intersection possible")

        return TimeWindow(
            from_date=max(self.from_date, other.from_date),
            to_date=min(self.to_date, other.to_date),
        )

    def union(self, other: "TimeWindow"):
        if not self.intersects(other):
            raise ValueError("No union possible")

        return TimeWindow(
            from_date=min(self.from_date, other.from_date),
            to_date=max(self.to_date, other.to_date),
        )

    @classmethod
    def around(cls, dt: datetime, td_window: TimeDeltaWindow) -> "TimeWindow":
        fr, to = None, None

        if td_window.lower is not None:
            fr = dt - td_window.lower

        if td_window.upper is not None:
            to = dt + td_window.upper

        return cls(fr, to)

    @classmethod
    def around_now(cls, td: timedelta) -> "TimeWindow":
        td_window = TimeDeltaWindow(td, td)
        return cls.around(time_now(), td_window)

    def dates(self) -> Generator[datetime, None, None]:
        return self.range(timedelta(days=1))

    def range(self, td: timedelta) -> Generator[datetime, None, None]:
        temp_date = self.from_date

        while temp_date <= self.to_date:
            yield temp_date
            temp_date += td
