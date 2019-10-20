# -*- coding:utf-8 -*-
import pytest

from anywhere.protobuf3 import load, serialize
from anywhere import testsets


@pytest.mark.parametrize(
    'where_obj',
    testsets.WHERES,
    ids=[str(i) for i in range(1, len(testsets.WHERES) + 1)],
)
def test_load_serialize(where_obj):
    where_obj2 = load(serialize(where_obj))

    assert id(where_obj) != id(where_obj2)
    assert where_obj == where_obj2
