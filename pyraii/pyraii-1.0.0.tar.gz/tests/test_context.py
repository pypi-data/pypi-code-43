#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `pyraii` package."""
import pytest
from mock_closable import MockClosable
from pyraii.context import closing_on_exception, closing_nothrow, closing_multiple
from mock_exception import MockException, DifferentMockException


@pytest.fixture
def mock_closable():
    return MockClosable()


@pytest.fixture
def multiple_mock_closables():
    return [MockClosable(), MockClosable(), MockClosable(), MockClosable()]


def test_closing_on_exception_no_exception(mock_closable):
    with closing_on_exception(mock_closable):
        pass
    assert not mock_closable.is_closed
    assert mock_closable.times_closed == 0


def test_closing_on_exception_any_exception(mock_closable):
    with pytest.raises(MockException):
        with closing_on_exception(mock_closable):
            raise MockException()
    assert mock_closable.is_properly_closed


def test_closing_on_exception_exact_exception(mock_closable):
    with pytest.raises(MockException):
        with closing_on_exception(mock_closable, MockException):
            raise MockException()
    assert mock_closable.is_properly_closed


def test_closing_on_exception_different_exception(mock_closable):
    with pytest.raises(DifferentMockException):
        with closing_on_exception(mock_closable, MockException):
            raise DifferentMockException()
    assert not mock_closable.is_closed
    assert mock_closable.times_closed == 0


def test_closing_nothrow_no_exception(mock_closable):
    with closing_nothrow(mock_closable):
        pass
    assert mock_closable.is_properly_closed


def test_closing_nothrow_with_exception(mock_closable):
    mock_closable.exception_on_close = MockException()
    with closing_nothrow(mock_closable):
        pass
    assert mock_closable.is_properly_closed


def test_closing_nothrow_no_exception(mock_closable):
    with closing_nothrow(mock_closable):
        pass
    assert mock_closable.is_properly_closed


def test_closing_multiple_without_exception(multiple_mock_closables):
    with closing_multiple(multiple_mock_closables):
        pass
    assert all([x.is_properly_closed for x in multiple_mock_closables])


def test_closing_multiple_with_exception(multiple_mock_closables):
    with pytest.raises(MockException):
        with closing_multiple(multiple_mock_closables):
            raise MockException()
    assert all([x.is_properly_closed for x in multiple_mock_closables])
