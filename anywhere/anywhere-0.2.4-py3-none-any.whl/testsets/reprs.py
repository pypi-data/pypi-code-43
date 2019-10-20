# -*- coding:utf-8 -*-
# pylint: disable=line-too-long

_BASE_REPRESENTATIONS = [
    "Primitive(field='f1', op='eq', value='value')",
    "Primitive(field='f1', op='eq', value=42)",
    "Primitive(field='f1', op='eq', value=3.14)",
    "Primitive(field='f1', op='eq', value=True)",
    "Condition(op=Operator.OR, values=[Primitive(field='f1', op='eq', value='aaa'), Primitive(field='f2', op='eq', value=5)])",
    "Condition(op=Operator.OR, values=[Primitive(field='f1', op='eq', value='aaa'), Primitive(field='f2', op='eq', value=5), Primitive(field='f1', op='eq', value='bbb')])",
    "Condition(op=Operator.AND, values=[Primitive(field='f1', op='eq', value='aaa'), Primitive(field='f2', op='eq', value=5)])",
    "Condition(op=Operator.AND, values=[Primitive(field='f1', op='eq', value='aaa'), Primitive(field='f2', op='eq', value=5), Primitive(field='f1', op='eq', value='bbb')])",
    "Condition(op=Operator.OR, values=[Condition(op=Operator.AND, values=[Primitive(field='f1', op='eq', value=50), Primitive(field='f2', op='eq', value='aaa')]), Primitive(field='f2', op='eq', value='bbb')])",
]

REPRESENTATIONS = _BASE_REPRESENTATIONS + [
    val.replace(
        "field='f1', op='eq", "field='f1', op='gt"
    ).replace(
        "field='f2', op='eq'", "field='f2', op='match'"
    )
    for val in _BASE_REPRESENTATIONS
]
