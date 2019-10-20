# -*- coding:utf-8 -*-
import operator

DEFAULT_OPERATORS = (
    ('eq', operator.eq),
    ('neq', operator.ne),
    ('gt', operator.gt),
    ('gte', operator.ge),
    ('lt', operator.lt),
    ('lte', operator.le),
)


class Field:
    # pylint: disable=too-few-public-methods

    _name: str = None

    def __init__(self, *, column=None, operators=DEFAULT_OPERATORS, extra_operators=None):
        ops = dict(operators)
        if extra_operators:
            ops.update(extra_operators)

        self.column = column
        self.operators = ops

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name is not None:
            raise RuntimeError('name already set')
        self._name = value
