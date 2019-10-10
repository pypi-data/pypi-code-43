""" Impetuous and actions invoked from argument parser.
"""

import datetime
import logging
import re
import subprocess

import colorama as ca
import dateutil.parser

import impetuous.data
from impetuous.config import CONFIG_DIR, CONFIG_INI_PATH, write_config
from impetuous.interaction import Field
from impetuous.sheet import EntryNotFoundError, localtz, utcnow

logger = logging.getLogger(__name__)

entry_fields = [
    Field('entry', f) for f in impetuous.data.tables['entry'].c.keys()
]

submission_fields = [
    Field('submission', f) for f in impetuous.data.tables['submission'].c.keys()
]


def maybe_elide(string, max_length):
    r"""
    >>> maybe_elide('Hello world', 4)
    'H...'
    >>> maybe_elide('Hello world', 5)
    'H...d'
    >>> maybe_elide('Hello world', 9)
    'Hel...rld'
    >>> maybe_elide('Hello world', 10)
    'Hell...rld'
    >>> maybe_elide('Hello world', 11)
    'Hello world'
    >>> maybe_elide('Spam and eggs!', 9)
    'Spa...gs!'
    >>> maybe_elide('Spam and eggs!', 10)
    'Spam...gs!'
    >>> maybe_elide('We have phasers, I vote we blast \'em!   -- Bailey, "The Corbomite Maneuver", stardate 1514.2', 29)
    'We have phase...ardate 1514.2'

    # If this happens, we act stupid. But at least we don't crash so Brandon won't
    # submit tracebacks to the issue tracker.
    >>> maybe_elide('Hello world', -1)
    ''
    >>> maybe_elide('Hello world', 0)
    ''
    >>> maybe_elide('Hello world', 1)
    '.'
    >>> maybe_elide('Hello world', 2)
    '..'
    >>> maybe_elide('Hello world', 3)
    '...'

    """
    if len(string) > max_length:
        if max_length < 0:
            return ""
        elif max_length < 4:
            return "..."[:max_length]

        chunklen = (max_length - 3) // 2
        return "{}...{}".format(string[:chunklen + 1],
                                '' if chunklen == 0 else string[-chunklen:])
    else:
        return string


def one_line(string):
    r"""
    Sanitize for one-line printing?

    >>> sanitize('foo\nbar\tbaz')
    'foo bar baz'

    """
    return string.replace('\t', ' ').replace('\n', ' ')


def get_terminal_width():
    """
    Return the terminal width as an integer or None if we can't figure it out.
    """
    try:
        stty = subprocess.check_output(['stty', 'size'])
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    else:
        try:
            return int(stty.strip().split(b' ')[1])
        except (ValueError, IndexError):
            pass
    try:
        tput = subprocess.check_output(['tput', 'cols'])
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    else:
        try:
            return int(tput.strip())
        except ValueError:
            pass
    try:
        env = subprocess.check_output('echo -n $COLUMNS', shell=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    else:
        try:
            return int(env)
        except ValueError:
            pass


def parse_friendly_datetime(value, default=utcnow().astimezone(localtz), **kwargs):
    """
    Only really seems to know what UTC and your local time zone is, everything
    else it'll ignore and we pretend like it's your local timezone ...

    >>> parse_friendly_datetime("1-1-2008 13:00:09")
    datetime.datetime(2008, 1, 1, 13, 0, 9, tzinfo=tzlocal())
    """
    if value == 'now':
        return default
    elif value == 'today':
        # If value is not your time zone then ... yikes!
        return default.replace(hour=0, minute=0, second=0, microsecond=0)
    elif value == 'tomorrow':
        # If value is not your time zone then ... yikes!
        return parse_friendly_datetime('today') + datetime.timedelta(days=1)
    elif value == 'yesterday':
        # If you say yesterday, what time of the day does that mean? The start
        # of the day? Or the current time but a day ago? Probably depends on
        # context?
        # `im --since yesterday show` vs `im doing great --when yesterday `
        return (default - datetime.timedelta(days=1)
                ).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        dt = dateutil.parser.parse(value, **kwargs)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=localtz)
        else:
            return dt
