# -*- coding: future_fstrings -*-
import errno
import os
import sys
import time
from abc import abstractmethod
from datetime import datetime, timedelta
import dateutil.parser

if sys.version_info > (3, 2):
    from datetime import timezone
    utc = timezone.utc
else:
    from datetime import tzinfo
    ZERO = timedelta(0)

    class UTC(tzinfo):

        def utcoffset(self, dt):
            return ZERO

        def tzname(self, dt):
            return "UTC"

        def dst(self, dt):
            return ZERO

    utc = UTC()


def create_dir(dirpath):
    try:
        os.mkdir(dirpath)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_current_timestamp(milliseconds=False):
    # The time.time() function returns the number of seconds since the epoch, as seconds. Note that the "epoch" is defined as the start of January 1st, 1970 in UTC.
    if milliseconds:
        return int(time.time()*1000)
    else:
        return int(time.time())


def convert_epoch_to_utc_date(timestamp, date_format="%Y-%m-%d %H:%M:%S", milliseconds=False):
    try:
        if milliseconds:
            timestamp = timestamp/1000.0
        date_str = datetime.utcfromtimestamp(timestamp).strftime(date_format)
    except Exception as e:
        raise Exception(f'''Error in converting timestamp {timestamp}''')

    return date_str


def convert_utc_date_to_epoch(datestr, date_format='%Y-%m-%dT%H:%M:%S.%fZ', milliseconds=False):
    epoch = datetime(1970, 1, 1)
    timestamp = (datetime.strptime(datestr, date_format) - epoch).total_seconds()
    if milliseconds:
        timestamp = timestamp*1000
    return int(timestamp)


def convert_date_to_epoch(datestr):
    dateobj = dateutil.parser.parse(datestr)
    if sys.version_info > (3, 3):
        return dateobj.timestamp()
    else:
        return (dateobj - datetime(1970, 1, 1, tzinfo=utc)).total_seconds()


def get_datetime_from_isoformat(date_str):
    return dateutil.parser.parse(date_str)


def get_current_datetime():
    return datetime.now(tz=utc)


def addminutes(date_obj, num_minutes):
    new_date_obj = date_obj + timedelta(minutes=num_minutes)
    return new_date_obj.isoformat()


def merge_dict(dict1, dict2):
    for k, v in dict2.items():
        if k in dict1:
            dict1[k].update(v)
        else:
            dict1[k] = v
    return dict1


def compatibleabstractproperty(func):

    if sys.version_info > (3, 3):
        return property(abstractmethod(func))
    else:
        from abc import abstractproperty
        return abstractproperty(func)


def get_normalized_path(path):
    return os.path.realpath(os.path.abspath(os.path.expanduser(path)))
