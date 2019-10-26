from datetime import timedelta

import pandas as pd
from dateutil import rrule
from recurrent import RecurringEvent


def format_date(date) -> str:
    return format(date, "%Y-%m-%d")


def get_today():
    return pd.Timestamp("today").normalize()


def get_next_year():
    return (get_today() + timedelta(days=365)).normalize()


def get_dates(frequency, start=None, end=None):
    start = start or get_today()
    end = end or get_next_year()

    try:
        return [pd.Timestamp(frequency).normalize()]
    except ValueError:
        pass

    try:
        event = RecurringEvent()
        event.parse(frequency)
        rule = rrule.rrulestr(event.get_RFC_rrule())
        return [
            pd.to_datetime(date).normalize()
            for date
            in rule.between(start, end)
        ]
    except ValueError as e:
        raise ValueError("Could not parse frequency:" + frequency)
