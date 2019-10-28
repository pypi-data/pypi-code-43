"""
KomaPy extension plots.
"""

import uuid
import datetime
from collections import Callable

from .client import fetch_bma_as_dataframe
from .exceptions import ChartError
from .processing import dataframe_or_empty
from .utils import resolve_timestamp

__all__ = [
    'register_extension',
]

extension_registers = {
    'explosion': {
        'resolver': 'plot_explosion_line',
        'label': '',
    },
    'dome': {
        'resolver': 'plot_dome_appearance',
        'label': '',
    },
}


def register_extension(name, resolver, **kwargs):
    """
    Register extension plot function to the supported extensions data.
    """
    if not isinstance(resolver, Callable):
        raise ChartError('Extension plot resolver must be callable')

    if name in extension_registers:
        raise ChartError('Extension plot name already exists')

    extension_registers[name] = dict(resolver=resolver, **kwargs)


def plot_explosion_line(axis, starttime, endtime, **options):
    """
    Plot Merapi explosion line on current axis.

    Exposion date is fetched from seismic bulletin database. All event dates
    are treated as local timezone, i.e. Asia/Jakarta.
    """
    handle = None
    date_format = r'%Y-%m-%d %H:%M:%S'

    params = {
        'eventtype': 'EXPLOSION',
        'nolimit': True,
        'eventdate__gte': starttime.strftime(date_format),
        'eventdate__lt': endtime.strftime(date_format),
        'request_id': uuid.uuid4().hex
    }
    data = fetch_bma_as_dataframe('bulletin', **params)

    eventdate = resolve_timestamp(dataframe_or_empty(data, 'eventdate'))
    if eventdate.empty:
        return handle

    for timestamp in eventdate:
        handle = axis.axvline(timestamp, **options)

    return handle


def plot_dome_appearance(axis, starttime, endtime, **options):
    """
    Plot Merapi dome appearance on current axis.

    Merapi dome appears at 2018-08-01 Asia/Jakarta timezone.
    """
    handle = None
    start = starttime.replace(tzinfo=None)
    end = endtime.replace(tzinfo=None)

    timestamp = datetime.datetime(2018, 8, 1)
    if start <= timestamp and timestamp <= end:
        handle = axis.axvline(timestamp, **options)
    return handle
