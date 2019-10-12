from datetime import datetime
from datetime import timedelta
from typing import Optional

from pytz import timezone


LA_TZ_NAME = 'America/Los_Angeles'


def format_percentage(x: float) -> str:
    return '{:,.2%}'.format(x)


def format_price(x: float, empty_for_zero: bool = False) -> str:
    r = '${:,.2f}'.format(x)
    if empty_for_zero and r == '$0.00':
        return '-'

    return r


def format_optional_price(x: Optional[float]) -> str:
    if x is None:
        return '-'
    else:
        return format_price(x=x)


def format_quantity(x: float) -> str:
    return '{:,.0f}'.format(x)


def format_greek(x: float) -> str:
    return '{:,.2}'.format(x)


def format_optional_greek(x: Optional[float]) -> str:
    if x is None:
        return '-'
    else:
        return format_greek(x=x)


def attach_timezone(t: datetime) -> datetime:
    return t.astimezone(tz=timezone(LA_TZ_NAME))


def parse_date(s: str) -> datetime:
    return datetime.strptime(s, '%Y-%m-%d').astimezone(tz=timezone(LA_TZ_NAME))


def parse_datetime(s: str) -> datetime:
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').astimezone(tz=timezone(LA_TZ_NAME))


def parse_datetime_with_microsecond(s: str) -> datetime:
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ').astimezone(tz=timezone(LA_TZ_NAME))


def parse_datetime_with_optional_microsecond(s: str) -> datetime:
    try:
        return parse_datetime_with_microsecond(s)
    except ValueError:
        return parse_datetime(s)


def parse_optional_float(s: Optional[str]) -> Optional[float]:
    return s if s is None else float(s)


def parse_optional_int(s: Optional[str]) -> Optional[int]:
    return s if s is None else int(s)


def get_week(d: datetime) -> str:
    _d = d - timedelta(days=d.weekday())
    return _d.strftime('%Y-%m-%d')


def get_month(d: datetime) -> str:
    _d = d - timedelta(days=(d.day - 1))
    return _d.strftime('%Y-%m-%d')
