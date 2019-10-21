# -*- coding:utf-8 -*-
from copy import deepcopy
from itertools import combinations_with_replacement

import pytest

from anywhere import testsets


@pytest.mark.parametrize(
    'where_obj,string',
    zip(
        testsets.WHERES,
        testsets.STRINGS,
    ),
    ids=[str(i) for i in range(1, len(testsets.WHERES) + 1)],
)
def test_str(where_obj, string):
    assert str(where_obj) == string


@pytest.mark.parametrize(
    'where_obj,representation',
    zip(
        testsets.WHERES,
        testsets.REPRESENTATIONS,
    ),
    ids=[str(i) for i in range(1, len(testsets.WHERES) + 1)],
)
def test_repr(where_obj, representation):
    assert repr(where_obj) == representation


@pytest.mark.parametrize(
    'where_obj1,where_obj2',
    combinations_with_replacement(testsets.WHERES, 2),
    ids=lambda _: '',
)
def test_comparision(where_obj1, where_obj2):
    if id(where_obj1) == id(where_obj2):
        # We are comparing the same object, should be equal
        assert where_obj1 == where_obj2
    else:
        assert where_obj1 != where_obj2


@pytest.mark.parametrize(
    'where_obj',
    testsets.WHERES,
    ids=[str(i) for i in range(1, len(testsets.WHERES) + 1)],
)
def test_comparision_deepcopy(where_obj):
    where_obj2 = deepcopy(where_obj)

    assert id(where_obj) != id(where_obj2)
    assert where_obj == where_obj2
