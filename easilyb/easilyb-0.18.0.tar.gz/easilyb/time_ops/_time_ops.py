from time import gmtime, time, strptime, strftime, mktime, timezone
from calendar import timegm

import logging
logger = logging.getLogger(__name__)

UTC_ISO8601_TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
UTC_ISO8601_DATE_FORMAT = "%Y-%m-%d"


def epoch_to_iso8601(timestamp):
    try: mlsec = str(timestamp).split('.')[1][:3]
    except: mlsec = "000"
    mlsec = mlsec + "0"*(3-len(mlsec))
    iso_str = strftime("%Y-%m-%dT%H:%M:%S.{}Z".format(mlsec), gmtime(timestamp))
    return iso_str


def iso8601_to_epoch(iso_str):
    str_time, mlsec = iso_str.split('.')
    mlsec = float(mlsec[:-1])/1000
    time_tuple = strptime(str_time+"UTC", "%Y-%m-%dT%H:%M:%S%Z")
    return mktime(time_tuple) - timezone + mlsec


def epoch_to_pathfriendly(timestamp=None):
    if timestamp is None: timestamp = time()
    return strftime("%Y%m%d%H%M%S", gmtime(timestamp))


def format_utc_time(timestamp=None, format=UTC_ISO8601_TIME_FORMAT):
    if timestamp is None:
        timestamp = time()
    return strftime(format, gmtime(timestamp))


def parse_utc_time(string, format=UTC_ISO8601_TIME_FORMAT):
    return timegm(strptime(string, format))


def format_utc_date(timestamp=None, format=UTC_ISO8601_DATE_FORMAT):
    if timestamp is None:
        timestamp = time()
    return format_utc_time(timestamp, format)


def parse_utc_date(string, format=UTC_ISO8601_DATE_FORMAT):
    return parse_utc_time(string, format)