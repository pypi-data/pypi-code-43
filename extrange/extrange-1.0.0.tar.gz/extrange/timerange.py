import datetime

def _require_subclass_of(cls, v):
    if not issubclass(type(v), cls):
        msg = 'A {} is required but got a {}.'.format(cls, type(v))
        raise TypeError(msg)

def _must_time(v):
    _require_subclass_of(datetime.time, v)


class TimeRange:
    '''
    Represents range of two times as [begin, end).

    If BEGIN > END, it means over midnight likes 22:00 to 06:00 of next day.
    Both of begin and end can be None. It represents 00:00/24:00.
    So [None, 22:00) is before 22:00. [06:00, None) is after 06:00.
    And [None, None) is entire of day.

    TimeRange implements collections.abc.Container
    '''

    def __init__(self, begin, end):
        if begin is not None:
            _must_time(begin)
        if end is not None:
            _must_time(end)

        self.begin = begin
        self.end = end

    def __contains__(self, v):
        _must_time(v)

        begin = self.begin
        end = self.end

        if begin is None and end is None:
            return True
        if begin is None:
            return v < end
        if end is None:
            return v >= begin

        if begin > end:
            return v < end or v >= begin
        return begin <= v < end

    def __str__(self):
        return repr(self)

    def __repr__(self):
        typename = type(self).__name__
        return '{}({}, {})'.format(typename, repr(self.begin), repr(self.end))
