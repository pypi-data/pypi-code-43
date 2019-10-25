# -*- coding: utf-8 -*-

from __future__ import division

from .colors import dim


NA_VALUE = dim("-")


class BaseBehavior(object):
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __unicode__(self):
        return u"{}({})".format(self.__class__.__name__, self.fieldname)

    def __str__(self):
        return self.__unicode__()

    def __call__(self, values):
        return NotImplemented


class Variables(BaseBehavior):
    def __unicode__(self):
        return u"Variables"

    def __call__(self, variables):
        # /!\ variables must be a list of pairs
        return " ".join(["{}={}".format(k, v) for k, v in variables])


class SingleValue(BaseBehavior):
    def __unicode__(self):
        return self.fieldname

    def __call__(self, values):
        assert len(values) <= 1
        return values[0] if values else NA_VALUE


class ArithmeticBehavior(BaseBehavior):
    pass


class Sum(ArithmeticBehavior):
    def __call__(self, values):
        return sum(values) if values else NA_VALUE


class Count(ArithmeticBehavior):
    def __call__(self, values):
        return len(values)


class List(BaseBehavior):
    def __call__(self, values):
        if not values:
            return NA_VALUE

        return " ".join([str(v) for v in values])


class Min(ArithmeticBehavior):
    def __call__(self, values):
        return min(values) if values else NA_VALUE


class Max(ArithmeticBehavior):
    def __call__(self, values):
        return max(values) if values else NA_VALUE


class Avg(ArithmeticBehavior):
    def __call__(self, values):
        if values:
            return sum(values) / len(values)

        return NA_VALUE


class Median(ArithmeticBehavior):
    def __call__(self, values):
        # Backported from python3 statistics.median
        data = sorted(values)
        n = len(data)
        if n == 0:
            return NA_VALUE
        if n % 2 == 1:
            return data[n // 2]
        else:
            i = n // 2
            return (data[i - 1] + data[i]) / 2
