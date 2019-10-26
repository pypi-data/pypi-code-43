import calendar
import datetime
import dateutil.parser
import dateutil.relativedelta
import dateutil.rrule
import pytz
import re

ONE_MONTH_IN_DAYS = 30
ONE_DAY_IN_MILLISECONDS = 86400000
HALF_AN_HOUR_IN_SECONDS = 1800


def current_time():
    return as_utc(datetime.datetime.utcnow())


def as_utc(time):
    return as_time_zone(time, pytz.utc)


def as_time_zone(time, time_zone):
    return time_zone.normalize(time_zone.localize(time))


def to_utc(time):
    return to_time_zone(time, pytz.utc)


def date_to_time(date, time_zone=pytz.UTC):
    time = datetime.datetime.combine(date, datetime.time.min)
    if not time_zone:
        return time
    return as_time_zone(time, time_zone)


def as_time_zone_aware(naive_time):
    if type(naive_time) == datetime.date:
        return date_to_time(naive_time, pytz.UTC)
    elif naive_time.tzinfo is None:
        return as_time_zone(naive_time, pytz.UTC)
    else:
        return naive_time


def to_time_zone(time, time_zone):
    return time.astimezone(time_zone)


def to_timestamp(time):
    return calendar.timegm(to_utc(time).timetuple())


def from_timestamp(timestamp):
    return as_utc(datetime.datetime.utcfromtimestamp(timestamp))


def day_of(time):
    return date_to_time(time.date(), time.tzinfo)


def day_before(day, n=1):
    return date_to_time(day.date() - datetime.timedelta(n), day.tzinfo)


def day_after(day, n=1):
    return date_to_time(day.date() + datetime.timedelta(n), day.tzinfo)


def days_after(since, until):
    day = day_of(since)
    until = day_of(until)
    while day < until:
        yield day
        day = day_after(day)


def days_before(until, since):
    day = day_before(day_of(until))
    since = day_of(since)
    while day >= since:
        yield day
        day = day_before(day)


def end_of_day(date):
    return int(
        round(calendar.timegm(date.timetuple()) * 1000)) + 24 * 60 * 60 * 1000


def render_time(time):
    return time.isoformat()


def render_date(time):
    return time.isoformat().split('T')[0]


def parse_time(string):
    return dateutil.parser.parse(string)


class Period(object):
    PERIOD_PATTERN = re.compile(r'^(?P<value>\d+)(?P<unit>[yqmwdHMS])$')

    def __init__(self, value=1, unit='d'):
        if not isinstance(value, int) or value <= 0:
            raise ValueError('invalid period value %r' % value)

        if unit == 'y':
            self.delta = datetime.timedelta(years=value)
        elif unit == 'q':
            self.delta = dateutil.relativedelta.relativedelta(months=3 * value)
        elif unit == 'm':
            self.delta = dateutil.relativedelta.relativedelta(months=value)
        elif unit == 'w':
            self.delta = datetime.timedelta(weeks=value)
        elif unit == 'd':
            self.delta = datetime.timedelta(days=value)
        elif unit == 'H':
            self.delta = datetime.timedelta(hours=value)
        elif unit == 'M':
            self.delta = datetime.timedelta(minutes=value)
        elif unit == 'S':
            self.delta = datetime.timedelta(seconds=value)
        else:
            raise ValueError('invalid period unit %r' % unit)

        self.value = value
        self.unit = unit

    def round_down(self, time):
        if self.unit == 'y':
            return time - dateutil.relativedelta.relativedelta(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.unit == 'q':
            time_zone = time.tzinfo
            naive_time = date_to_time(time.date(), time_zone=None)
            quarters = dateutil.rrule.rrule(
                dateutil.rrule.MONTHLY,
                bymonth=(1, 4, 7, 10),
                bysetpos=-1,
                dtstart=datetime.datetime(naive_time.year, 1, 1),
                count=8)
            return as_time_zone(
                quarters.before(
                    naive_time + dateutil.relativedelta.relativedelta(days=1)),
                time_zone)
        elif self.unit == 'm':
            return time - dateutil.relativedelta.relativedelta(
                day=1, hour=0, minute=0, second=0, microsecond=0)
        elif self.unit == 'w':
            return time - dateutil.relativedelta.relativedelta(
                weekday=dateutil.relativedelta.MO(-1),
                hour=0, minute=0, second=0, microsecond=0)
        elif self.unit == 'd':
            return time - dateutil.relativedelta.relativedelta(
                hour=0, minute=0, second=0, microsecond=0)
        elif self.unit == 'H':
            return time - dateutil.relativedelta.relativedelta(
                minute=0, second=0, microsecond=0)
        elif self.unit == 'M':
            return time - dateutil.relativedelta.relativedelta(
                second=0, microsecond=0)
        elif self.unit == 'S':
            return time - dateutil.relativedelta.relativedelta(microsecond=0)

    def seconds(self):
        return self.delta.total_seconds()

    def intervals(self, start_time, end_time=None):
        if end_time is None:
            end_time = current_time()

        start = self.round_down(start_time)
        end = start + self.delta
        while end <= end_time:
            yield start, end
            start = end
            end += self.delta

    def __repr__(self):
        return 'Period(%r, %r)' % (self.value, self.unit)

    def __str__(self):
        return '%d%s' % (self.value, self.unit)

    def __eq__(self, other):
        return self.value == other.value and self.unit == other.unit

    def __hash__(self):
        return hash((self.value, self.unit))

    @classmethod
    def from_string(cls, string):
        match = re.match(cls.PERIOD_PATTERN, string)
        if match is None:
            raise ValueError('invalid period string %r' % string)

        value = int(match.group('value'))
        unit = match.group('unit')

        return Period(value, unit)
