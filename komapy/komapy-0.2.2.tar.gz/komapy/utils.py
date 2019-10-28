"""
KomaPy utility module.
"""

import base64
import re
import uuid

import pytz
from dateutil import parser

import pandas as pd


def resolve_timestamp(data):
    """
    Resolve data timestamp.
    """
    if data.empty:
        return data

    data = pd.to_datetime(data)
    return data


def to_pydatetime(*args, **kwargs):
    """
    Convert date string to Python datetime. If date string contains a timezone
    info, it will return datetime aware. If timezone argument is provided, it
    will convert current timezone from date string to timezone in the argument.
    """
    timezone = kwargs.pop('timezone', None)
    date_obj = parser.parse(*args, **kwargs)
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc
    if date_obj.tzinfo:
        return date_obj.astimezone(tz)
    return tz.localize(date_obj)


def to_pydatetime_from_dictionary(data, keys):
    """Convert date string to Python datetime whose key in keys."""
    return [
        dict(
            (key, to_pydatetime(value) if key in keys else value)
            for key, value in item.items()
        ) for item in data
    ]


def generate_url_safe_filename(extension='png'):
    """Generate URL-safe random filename based on UUID4."""
    name = uuid.uuid4()
    filename = base64.urlsafe_b64encode(
        name.bytes).decode('utf-8').rstrip('=\n')
    return '{filename}.{extension}'.format(
        filename=filename, extension=extension)


def compute_middletime(starttime, endtime):
    """Calculate middle time between two timestamp."""
    if isinstance(starttime, str):
        start = to_pydatetime(starttime)
    else:
        start = starttime

    if isinstance(endtime, str):
        end = to_pydatetime(endtime)
    else:
        end = endtime
    delta = (end - start) / 2.0
    return start + delta


def compute_middletime_from_list(starttime, endtime):
    """Calculate middle time between two list of timestamps."""
    return [
        compute_middletime(start, end)
        for start, end in zip(starttime, endtime)
    ]


def time_to_offset(starttime, endtime, middletime):
    """Transform middle time to offset."""
    nominator = (middletime - starttime).total_seconds()
    denominator = (endtime - starttime).total_seconds()
    return float(nominator) / float(denominator)


def get_validation_methods(root_class):
    """Get all validation metods in the root class."""
    re_validate_template = re.compile(r'validate_(?P<name>\w+)')

    validation_methods = []
    for item in root_class.__dict__:
        matched = re_validate_template.match(item)
        if matched:
            name = matched.groupdict().get('name')
            method_name = 'validate_{}'.format(name)
            validation_methods.append(method_name)

    return validation_methods
