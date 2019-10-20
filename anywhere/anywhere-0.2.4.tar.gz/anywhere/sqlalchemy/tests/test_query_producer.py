# -*- coding:utf-8 -*-
import pytest

from anywhere import testsets
from . import testset as local_testset


@pytest.mark.parametrize(
    'where_obj,expected_query',
    zip(
        testsets.WHERES,
        local_testset.QUERIES,
    ),
    ids=[str(i) for i in range(1, len(testsets.WHERES) + 1)],
)
def test_produce_query(where_obj, expected_query, query_producer):
    parsed = query_producer.query_from_where(where_obj)

    assert str(parsed) == str(expected_query)
