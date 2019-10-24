import numpy as np
import datetime
import holidays
from datetime import timedelta
from argparse import ArgumentParser


def get(**kwars):
    try:
        date = kwars['startDate']
        days = kwars['days']
    except Exception as e:
        return e

    days_in_period = kwars.get('period', 30)
    active_holidays = kwars.get('holidays', True)
    active_sundays = kwars.get('sundays', True)

    date_format = "%Y-%m-%d"
    date = datetime.datetime.strptime(date, date_format).date()
    period = int(np.ceil(np.floor(days/days_in_period)))
    dates = [[date + timedelta(days=i), 0]
             for i in range(days_in_period*period)]
    for i in range(period):
        key = ((i+1) * days_in_period) - 1
        last_day_to_pay = dates[key][0]
        up_d = []
        x = 0
        next_x_day = next_day(
            last_day_to_pay, active_holidays, active_sundays, x)
        final_key = key + next_x_day
        if with_keys(key + next_x_day, dates) is False:
            up_d = up_days(next_x_day, last_day_to_pay)
            dates = dates + up_d
            final_key = key + len(up_d)

        dates[final_key][1] = 1

    return [[date.strftime(date_format), flag] for date, flag in dates]


def with_keys(new_keys, list_):
    return len(list_) > new_keys


def is_holiday(date):
    return date in holidays.CO()


def is_sunday(date):
    return date.strftime('%A') == 'Sunday'


def next_day(date, active_holidays, active_sundays, x):
    if active_holidays and active_sundays and (is_holiday(date) or is_sunday(date)):
        x = x + 1
        date = date + timedelta(days=1)
        return next_day(date, active_holidays, active_sundays, x=x)
    return x


def up_days(days, date):
    return [[date + timedelta(days=i), 0] for i in range(days,days + 1)]
