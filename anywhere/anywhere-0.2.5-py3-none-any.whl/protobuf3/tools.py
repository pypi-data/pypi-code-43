# -*- coding:utf-8 -*-
"""
Protocol buffers utils.
"""
import typing

from anywhere import base_types as bt
from . import anywhere_pb2 as pb


def serialize(where: typing.Union[bt.Primitive, bt.Condition]) -> pb.Where:
    """

    :param where:
    :return:
    """
    # pylint: disable=no-member
    msg = pb.Where()

    if isinstance(where, bt.Primitive):
        msg.primitive_value.field = where.field
        msg.primitive_value.op = where.op

        if isinstance(where.value, bool):
            msg.primitive_value.bool_value = where.value
        elif isinstance(where.value, int):
            msg.primitive_value.int_value = where.value
        elif isinstance(where.value, float):
            msg.primitive_value.double_value = where.value
        else:
            msg.primitive_value.string_value = where.value
    else:
        msg.condition_value.op = pb.Operator.AND if where.op == bt.Operator.AND else pb.Operator.OR
        msg.condition_value.values.extend([
            serialize(v) for v in where.values
        ])

    return msg


def load(msg: pb.Where) -> typing.Union[bt.Primitive, bt.Condition]:
    """

    :param msg:
    :return:
    """
    if msg.HasField('primitive_value'):
        val = msg.primitive_value

        value_variant = val.WhichOneof('value')
        where = bt.Primitive(msg.primitive_value.field, msg.primitive_value.op, getattr(val, value_variant))
    else:
        val = msg.condition_value

        if val.op == pb.Operator.AND:
            operator = bt.Operator.AND
        else:
            operator = bt.Operator.OR

        where = bt.Condition(operator, [load(v) for v in val.values])

    return where
