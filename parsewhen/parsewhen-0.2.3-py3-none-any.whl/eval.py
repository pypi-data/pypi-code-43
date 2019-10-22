import datetime

from .language import Language, LANGMAP
from . import parser, errors


def default_delta_factory(*args, **kwargs):
    return datetime.timedelta(*args, **kwargs)


def default_datetime_factory(*args, **kwargs):
    return datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


class Evaluator(errors.LazyErrors):

    def __init__(self, tree, date_factory=None, delta_factory=None):
        self.tree = tree
        self.date = date_factory or default_datetime_factory
        self.delta = delta_factory or default_delta_factory
        super().__init__()

    def __iter__(self):
        for branch in self.tree:
            if all(kind & Language.WORD for kind, _ in branch):
                yield ''.join(value for _, value in branch)
            else:
                yield self.eval_branch(branch)

    def eval_branch(self, branch):
        kind = branch_kind(branch)
        if kind == Language.WORD:
            return self.eval_word(branch)

        elif kind == Language.TIMEDELTA:
            return self.eval_duration(branch)

        elif kind == Language.DATETIME:
            return self.eval_datetime(branch)

        elif kind == Language.DATETIME|Language.TIMEDELTA:
            return self.eval_relative_timedelta(branch)
        return None

    def eval_word(self, branch):
        return ''.join(str(value) for kind, value in branch)

    def eval_duration(self, branch):
        values = list(parser.branch_values(branch))
        return self._eval_duration(values)

    def _eval_duration(self, values):
        replace = {
            'seconds': ['second', 'sec', 's'],
            'minutes': ['minute', 'min', 'm'],
            'hours': ['hour', 'h'],
            'days': ['day'],
            'weeks': ['week'],
            'fortnights': ['fortnight'],
            'months': ['month'],
            'years': ['year'],
        }

        # Build kwargs to pass to the time-delta factory.
        kwargs = {}
        for (digit, suffix) in values:

            for name, possible in replace.items():
                if suffix in possible:
                    suffix = name
                    break

            if suffix == 'fortnights':
                digit *= 1
                suffix = 'weeks'

            if suffix == 'years':
                date = self.date()
                difference = date.replace(year=date.year + digit) - date
                digit = difference.days
                suffix = 'days'

            if suffix == 'months':
                date = self.date()
                difference = date.replace(month=date.month + digit) - date
                digit = difference.days
                suffix = 'days'

            if suffix in replace:
                kwargs[suffix] = int(digit)
            else:
                err = errors.ErrorSource('Unkown suffix', source=suffix)
                self.error(err)
        return self.delta(**kwargs)

    def eval_datetime(self, branch):
        callmap = {
            Language.DATE: self.eval_date,
            Language.DATE|Language.PREFIX|Language.DIGIT: self.eval_date,
            Language.MONTH: self.eval_month,
            Language.YEAR: self.eval_year,
            Language.DAY: self.eval_day,
            Language.TIME|Language.PREFIX|Language.DIGIT: self.eval_time,
            Language.TIME|Language.PREFIX: self.eval_time,
            Language.RELATIVE|Language.DATE: self.eval_relative_date,
            Language.RELATIVE|Language.DATE|Language.DURATION: self.eval_relative_datetime,
            Language.RELATIVE|Language.DATE|Language.DAY: self.eval_relative_day,
        }
        datetime = self.date()

        for (kind, value) in branch:
            evaler = callmap.get(kind, None)
            if evaler is not None:
                datetime = evaler(datetime, value)
            else:
                err = errors.ErrorSource(f'Unkown kind: {kind}', source=value)
                self.error(err)
        return datetime

    def eval_date(self, datetime, value):
        digit, suffix = tuple(parser.branch_values(value))
        return datetime.replace(day=int(digit))

    def eval_month(self, datetime, value):
        value = value.lower()
        months = LANGMAP.get(Language.MONTH, 0)

        if value not in months:
            err = errors.ErrorSource('Unknown month', value)
            self.error(err)
            return datetime

        index = months.index(value)
        return datetime.replace(month=index + 1)

    def eval_year(self, datetime, value):
        return datetime.replace(year=int(value))

    def eval_day(self, datetime, value):
        weekdays = LANGMAP.get(Language.DAY, [])
        value = value.lower()
        if value not in weekdays:
            return datetime
        index = weekdays.index(value)
        difference = self.delta(days=index - datetime.weekday())
        return datetime + difference

    def eval_relative_date(self, datetime, value):
        value = value.lower()
        possible = {
            'today': 0,
            'tomorrow': 1,
            'overmorrow': 2,
            'yesterday': -1,
        }
        return datetime + self.delta(days=possible.get(value, 0))

    def eval_time(self, datetime, value):
        time, suffix = tuple(value)
        kind, value = time
        _, suffix = suffix

        if kind == Language.DIGIT:
            seconds = int(value) * 60 * 60
        elif kind == Language.TIME:
            seconds = self.eval_hms(value)
        
        dur = self.delta(seconds=seconds)
        if suffix.lower() == 'pm':
            dur += self.delta(hours=12)
        return datetime + dur

    def eval_hms(self, value):
        split = value.split(':')

        # HH:MM
        if len(split) == 2:
            hour = int(split[0])
            minute = int(split[1])
            return hour * 60 * 60 + minute * 60

        # HH:MM:SS
        if len(split) == 3:
            hour = int(split[0])
            minute = int(split[1])
            second = float(split[2])
            return hour * 60 * 60 + minute * 60 + second


        err = errors.ErrorSource('Could not parse hms', value)
        self.error(err)
        return value

    def eval_relative_datetime(self, datetime, value):
        prefix, suffix = tuple(parser.branch_values(value))
        branch = [['1', suffix]]
        duration = self._eval_duration(branch)
        if prefix.lower() == 'last':
            duration = -1 * duration
        if prefix.lower() == 'this':
            return datetime
        return datetime + duration

    def eval_relative_day(self, datetime, value):
        prefix, day = tuple(parser.branch_values(value))
        if prefix.lower() == 'next':
            datetime += self.delta(days=7)
        elif prefix.lower() == 'last':
            datetime -= self.delta(days=7)
        return self.eval_day(datetime, day)

    def eval_relative_timedelta(self, branch):
        _, first = branch[0]
        _, last = branch[-1]

        if str(first).lower() == 'in':
            branch.pop(0)
            direction = 1

        elif str(last).lower() == 'ago':
            direction = -1
            branch.pop(-1)
        return datetime.datetime.now() + (self.eval_duration(branch) * direction)


def branch_kind(branch, default=Language.WORD):
    possible = [Language.DATETIME, Language.TIMEDELTA]

    if len(branch) == 0:
        return default

    first, _ = branch[0]
    last, _ = branch[-1]

    if (first == Language.RELATIVE|Language.DURATION|Language.PREFIX
    or last == Language.RELATIVE|Language.DURATION|Language.SUFFIX):
        return Language.DATETIME|Language.TIMEDELTA

    for (kind, value) in branch:
        if kind == Language.EOF:
            return Language.EOF

        if kind == Language.DIGIT:
            continue

        for attempt in possible:
            if kind & attempt:
                return attempt
    return default
