# -*- coding:utf-8 -*-
_BASE_STRINGS = [
    "f1 eq 'value'",
    "f1 eq 42",
    "f1 eq 3.14",
    "f1 eq True",
    "(f1 eq 'aaa' | f2 eq 5)",
    "(f1 eq 'aaa' | f2 eq 5 | f1 eq 'bbb')",
    "(f1 eq 'aaa' & f2 eq 5)",
    "(f1 eq 'aaa' & f2 eq 5 & f1 eq 'bbb')",
    "((f1 eq 50 & f2 eq 'aaa') | f2 eq 'bbb')",
]

STRINGS = _BASE_STRINGS + [
    val.replace('f1 eq', 'f1 gt').replace('f2 eq', 'f2 match')
    for val in _BASE_STRINGS
]
