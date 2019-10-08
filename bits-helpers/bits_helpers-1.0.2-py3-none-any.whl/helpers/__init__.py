# -*- coding: utf-8 -*-
"""Helpers class file."""

import datetime

try:
    from builtins import xrange as range
except ImportError:
    from builtins import range


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def generate_gcs_object_name(base, prefix, extension='json'):
    """Return an object name for a new file in GCS."""
    # get current date in iso format
    now = datetime.datetime.now()
    isodate = datetime.datetime.isoformat(now)
    # create object name
    return '{}/{}_{}.{}'.format(base, prefix, isodate, extension)
