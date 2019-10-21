import datetime
from robotpt_common_utils import math_tools

NUM_DAYS_IN_A_WEEK = 7


def subtract_days(start_date, end_date):

    if (
            not (type(start_date) == type(end_date) == datetime.date)
            and not (type(start_date) == type(end_date) == datetime.datetime)
    ):
        raise TypeError("Inputs must be datetimes")

    return (end_date - start_date).days


def subtract_weeks(start_date, end_date, is_full_weeks_only=True):

    weeks_difference = subtract_days(start_date, end_date) / NUM_DAYS_IN_A_WEEK
    if is_full_weeks_only:
        return int(weeks_difference)
    else:
        return weeks_difference


def get_date_range(
        start_date,
        end_date,
        increment_days=1,
        output_format=None
):
    if not math_tools.is_int(increment_days):
        raise ValueError("'increment_days' must be an int")

    if increment_days < 0:
        raise ValueError("'increment_days' must be nonnegative")

    if start_date > end_date:
        raise IOError("'start_date' must be less than 'end_date'")

    date = start_date
    date_range = []
    while date < end_date:
        date_range.append(date)
        date += datetime.timedelta(days=increment_days)
    if output_format is None:
        return date_range
    elif type(output_format) is str:
        return [
            datetime.datetime.strftime(date, output_format)
            for date in date_range
        ]

