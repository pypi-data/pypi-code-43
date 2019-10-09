# -*-coding: utf-8-*-

import datetime as dt
import time
from datetime import datetime
from typing import Union

DEFAULT_FMT = '%Y-%m-%d %H:%M:%S'
NO_BLANK_FMT = '%Y%m%d%H%M%S'


def strftime(obj: Union[datetime, dt.date, None] = None, fmt: str = DEFAULT_FMT) -> str:
    """
    if obj, format obj to string.
    else format now time to string.
    :param obj:
    :param fmt:
    :return:
    """
    if obj and isinstance(obj, (datetime, dt.date)):
        return obj.strftime(fmt)
    return time.strftime(fmt)


def timestamp(precision: str = 's', returned_str: bool = False) -> Union[int, str]:
    """

    :param precision: s means seconds, ms means millisecond, others is not support
    :param returned_str: returned type is str or int
    :return:
    """
    origin = time.time()
    may_ms = origin * 1000 if precision == 'ms' else origin
    to_int = int(may_ms)
    return str(to_int) if returned_str else to_int


def _precision(precision: str):
    table = {
        ('second', 'S', 'Second', 's'): DEFAULT_FMT,
        ('M', 'minute', 'Minute'): '%Y-%m-%d %H:%M',
        ('H', 'hour', 'Hour'): '%Y-%m-%d %H',
        ('d', 'day', 'Day'): '%Y-%m-%d'
    }
    return table[tuple(filter(lambda x: precision in x, table.keys()))[0]]


def today(return_str: bool = True, precision: str = 'second') -> Union[str, dt.date]:
    """

    :param return_str:
    :param fmt:
    :return: 2019-08-10 16:23:17
    """
    t = dt.date.today()
    if return_str:
        return strftime(obj=t, fmt=_precision(precision))
    return t


def yesterday(return_str: bool = True, precision: str = 's') -> Union[str, dt.date]:
    y = today(return_str=False) + dt.timedelta(-1)
    if return_str:
        return strftime(obj=y, fmt=_precision(precision))
    return y

def last_month(fmt='%Y-%m'):
    last_day_of_last_month = dt.date.today().replace(day=1) - dt.timedelta(days=1)
    return last_day_of_last_month.strftime(fmt)


if __name__ == '__main__':
    print(last_month())
