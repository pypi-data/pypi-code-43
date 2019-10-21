# -*- coding:utf-8 -*-
from copy import deepcopy

from anywhere import base_types as bt


def replace_op(where):
    where = deepcopy(where)

    op_replacement = {
        'f1': 'gt',
        'f2': 'match',
    }
    if isinstance(where, bt.Primitive):
        where.op = op_replacement.get(where.field, 'eq')
    else:
        where.values = [
            replace_op(field) for field in where.values
        ]

    return where


_BASE_WHERES = [
    bt.Primitive(field='f1', op='eq', value='value'),
    bt.Primitive(field='f1', op='eq', value=42),
    bt.Primitive(field='f1', op='eq', value=3.14),
    bt.Primitive(field='f1', op='eq', value=True),
    bt.Condition(
        op=bt.Operator.OR,
        values=[
            bt.Primitive(field='f1', op='eq', value='aaa'),
            bt.Primitive(field='f2', op='eq', value=5)
        ]
    ),
    bt.Condition(
        op=bt.Operator.OR,
        values=[
            bt.Primitive(field='f1', op='eq', value='aaa'),
            bt.Primitive(field='f2', op='eq', value=5),
            bt.Primitive(field='f1', op='eq', value='bbb')
        ]
    ),
    bt.Condition(
        op=bt.Operator.AND,
        values=[
            bt.Primitive(field='f1', op='eq', value='aaa'),
            bt.Primitive(field='f2', op='eq', value=5)
        ]
    ),
    bt.Condition(
        op=bt.Operator.AND,
        values=[
            bt.Primitive(field='f1', op='eq', value='aaa'),
            bt.Primitive(field='f2', op='eq', value=5),
            bt.Primitive(field='f1', op='eq', value='bbb')
        ]
    ),
    bt.Condition(
        op=bt.Operator.OR,
        values=[
            bt.Condition(
                op=bt.Operator.AND,
                values=[
                    bt.Primitive(field='f1', op='eq', value=50),
                    bt.Primitive(field='f2', op='eq', value='aaa')
                ]
            ),
            bt.Primitive(field='f2', op='eq', value='bbb')
        ]
    ),
]

WHERES = _BASE_WHERES + [
    replace_op(where) for where in _BASE_WHERES
]
