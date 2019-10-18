#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from pyraii.close import close_nothrow, close_multiple, SomeCloseFailedException
from mock_closable import MockClosable
from mock_exception import MockException, DifferentMockException


def test_close_nothrow_no_exception():
    mock_closable = MockClosable()
    close_nothrow(mock_closable)
    assert mock_closable.is_properly_closed


def test_close_nothrow_on_exception():
    with pytest.raises(MockException):
        MockClosable(exception_on_close=MockException()).close()
    mock_closable = MockClosable(exception_on_close=MockException())
    close_nothrow(mock_closable)
    assert mock_closable.is_properly_closed


def test_close_multiple_order():
    a = MockClosable()
    b = MockClosable()
    c = MockClosable()
    close_multiple([a, b, c])
    assert all([x.is_properly_closed for x in [a, b, c]])
    assert a.relative_close_order > b.relative_close_order > c.relative_close_order


def test_close_multiple_exceptions():
    a = MockClosable()
    exception_1 = MockException()
    exception_2 = DifferentMockException()
    b = MockClosable(exception_on_close=exception_1)
    c = MockClosable()
    d = MockClosable(exception_on_close=exception_2)
    e = MockClosable()
    try:
        close_multiple([a, b, c, d, e])
    except SomeCloseFailedException as last_exception:
        assert (d, exception_2) in last_exception.resource_close_failings
        assert (b, exception_1) in last_exception.resource_close_failings
    else:
        assert False, "Should have thrown"

    assert all([x.is_properly_closed for x in [a, b, c, d, e]])
    assert a.relative_close_order > b.relative_close_order > c.relative_close_order > \
           d.relative_close_order > e.relative_close_order
