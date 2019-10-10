from dataclasses import dataclass
from datetime import datetime, time, date
from functools import total_ordering

tz_datetime = datetime


class TimezoneNotFound(Exception):
    pass


class TimezoneMismatch(Exception):
    pass


@dataclass(frozen=True)
class TimeDelta:
    hr: int = 0
    min: int = 0


@total_ordering
class MilitaryTime:
    def __init__(self, time, tzinfo):
        hr, min = divmod(time, 100)
        assert 0 <= min < 60
        assert 0 <= hr < 24

        self.hr = hr
        self.min = min
        self.tz = tzinfo

    @classmethod
    def from_hr_min(cls, hr: int, min: int, tzinfo):
        return cls(hr * 100 + min, tzinfo)

    @classmethod
    def extract_from_datetime(cls, dt: datetime):
        if not dt.tzinfo:
            raise TimezoneNotFound("No timezone present in datatime object")

        return cls.from_hr_min(dt.hour, dt.minute, dt.tzinfo)

    @property
    def time(self):
        return self.hr * 100 + self.min

    def to_time(self, tzinfo) -> time:
        return time(hour=self.hr, minute=self.min, tzinfo=tzinfo)

    def tz_unaware_time(self) -> time:
        return time(hour=self.hr, minute=self.min)

    def combine(self, dt: date) -> datetime:
        return self.tz.localize(datetime.combine(dt, self.tz_unaware_time()))

    def __eq__(self, other):
        return (self.hr, self.min, self.tz.zone) == (other.hr, other.min, other.tz.zone)

    def __str__(self):
        return f"{self.hr:02}{self.min:02}:{self.tz.zone}"

    def __repr__(self):
        return f"<MilitaryTime: {str(self)}>"

    def __add__(self, other: TimeDelta):
        min = (self.min + other.min) % 60
        additional_hrs = (self.min + other.min) // 60
        hr = (self.hr + other.hr + additional_hrs) % 24
        return MilitaryTime.from_hr_min(hr, min, self.tz)

    def __sub__(self, other: TimeDelta):
        min = (self.min - other.min) % 60
        additional_hrs = (self.min - other.min) // 60
        hr = (self.hr - other.hr + additional_hrs) % 24
        return MilitaryTime.from_hr_min(hr, min, self.tz)

    def __hash__(self):
        return hash((self.hr, self.min))

    def __lt__(self, other):
        if self.tz.zone != other.tz.zone:
            raise TimezoneMismatch(
                f"Recieved different timezones as {self.tz.zone} and {other.tz.zone}"
            )

        return (self.hr * 100, self.min) < (other.hr * 100, other.min)
