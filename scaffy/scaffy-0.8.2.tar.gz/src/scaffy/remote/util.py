# -*- coding: utf-8 -*-
""" Various utilities for the API cilent code. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from datetime import datetime


def parse_date(value):
    """ Parse a string containing a datetime.

    :param str value:
        A string containing a datetime, as returned by datetime.isoformat().
    :return datetime:
        `datetime` instance.
    """
    if not isinstance(value, datetime):
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
