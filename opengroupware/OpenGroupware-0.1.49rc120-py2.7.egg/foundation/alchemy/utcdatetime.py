#
# Copyright (c) 2009, 2013, 2014
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from datetime import tzinfo, timedelta, datetime, date
import sqlalchemy
import pytz

"""
Error Codes -
UTCDateTime100: type received unmappable type from application
UTCDateTime200: type received an unknown type from ORM
"""


class UniversalTimeZone(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)


# <http://stackoverflow.com/questions/414952/sqlalchemy-datetime-timezone>
# <http://blog.abourget.net/2009/4/27/sqlalchemy-and-timezone-support>
class UTCDateTime(sqlalchemy.types.TypeDecorator):
    impl = sqlalchemy.types.DateTime
    type = datetime

    def __init__(self, *arg, **kw):
        sqlalchemy.types.TypeDecorator.__init__(self, *arg, **kw)

    def process_bind_param(self, value, engine):
        '''should fire on "input"'''
        if value is None:
            return None
        elif isinstance(value, datetime):
            '''
            DateTime coming in from the database. One trick we do here is we
            clean up the microsecond value which some client's, particularly
            Objectivce-C code, does not like to see in the database - and we
            don't want it anyway.
            '''
            if value.tzinfo is None:
                value = value.replace(tzinfo=pytz.UTC)
            else:
                value = value.astimezone(pytz.UTC)
            if value.microsecond:
                value = value.replace(microsecond=0)
        elif isinstance(value, date):
            '''
            We are casting a date to a datetime.  There is inherent in this
            casting a potential for side-effects.  Perhaps we should log where
            this happens [if it happens], hunt this code down, and kill it with
            extreme prejudice.
            '''
            # TODO: Log this event?  Do we have a logger reference?
            value = datetime(
                value.year, value.month, value.day, tzinfo=pytz.UTC,
            )
        else:
            raise ValueError(
                'UTCDateTime100: Unexpected type "{0}" provided to '
                'UTCDateTime from application, this is a potential software '
                'bug or else a very badly behaved client.  Please report '
                'this message and stacktrace from this error to the '
                'project\'s bug tracker.\n'
                '<http://sourceforge.net/p/coils/tickets/>'.
                format(type(value), )
            )
        return value

    def process_result_value(self, value, engine):
        '''should fire on "output", taking the value from the database'''
        if (value is None):
            return None
        if isinstance(value, datetime):
            if not value.tzinfo:
                return pytz.UTC.localize(value)
            return value
        elif isinstance(value, date):
            '''
            Input is a DATE, not a datetime, this is a bit odd?  Why is a DATE
            value *in the database* mapped to a UTCDateTime type? Perhaps we
            should log this as a bug?
            '''
            # TODO: Log this event?  Do we havea logger reference?
            return datetime(
                value.year, value.month, value.day, tzinfo=pytz.UTC,
            )
        raise ValueError(
            'UTCDateTime200: Unexpected type "{0}" realized from ORM to '
            'UTCDateTime; this is a bug, please report this stacktrace and '
            'message to the project\'s bug tracker.\n'
            '<http://sourceforge.net/p/coils/tickets/>'.
            format(type(value), )
        )
