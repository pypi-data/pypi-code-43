import time
import math
import collections
import functools

from . import schedules


__all__ = ('create',)


class Valve:

    """
    You can only have `limit` of `key`'d values every `rate` seconds.
    """

    __slots__  = ('_schedule', '_bucket')

    def __init__(self, schedule, bucket = None):

        self._schedule = schedule

        self._bucket = bucket or []

    @property
    def bucket(self):

        """
        Get the bucket.
        """

        return self._bucket

    def count(self, key = None):

        """
        Get the number of values adhering to the key.
        """

        values = self._bucket

        return len(tuple(filter(key, values) if key else values))

    def left(self, limit, **kwargs):

        """
        Get the number of room left according to the limit.
        """

        return limit - self.count(**kwargs)

    def observe(self, value, delay):

        """
        Track value, wait for delay and discard it.
        """

        self._bucket.append(value)

        manage = functools.partial(self._bucket.remove, value)

        return self._schedule(delay, manage)

    def check(self, delay, limit, value, bypass = False, key = None):

        """
        Check if the valve is open. If it is, track value.
        Returns the number of spaces left before adding value.
        """

        left = self.left(limit, key = key)

        if bypass or left:

            self.observe(value, delay)

        return left


class Sling(Valve):

    """
    You can only have `limit` of `key`'d values every `delay` seconds.
    And I'm not gonna let you through unless you chill out first...
    So I will keep `trail` more values, discarding them `rate` quicker each.
    """

    __all__ = ()

    def check(self, delay, limit, trail, rate, value, key = None):

        """
        Check if the valve is open. Calculate delay and track state.
        """

        left = self.left(limit, key = key)

        delay *= ((left + trail) / limit) * rate

        self.observe(value, delay)

        left = max(left, 0)

        return left


def create(*args, loop = None, elastic = False, **kwargs):

    schedule = schedules.asyncio(loop) if loop else schedules.threading()

    cls = Sling if elastic else Valve

    valve = cls(schedule)

    check = functools.partial(valve.check, *args, **kwargs)

    return check
