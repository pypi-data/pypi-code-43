#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Dummy conftest.py for whattime.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    https://pytest.org/latest/plugins.html
"""
from datetime import datetime, timedelta
from typing import List

import pytest


@pytest.fixture(scope='session')
def now() -> datetime:
    return datetime.utcnow()


@pytest.fixture
def today_noon(now: datetime) -> datetime:
    return now.replace(hour=12, minute=0, second=0, microsecond=0)


@pytest.fixture
def monday(today_noon: datetime) -> datetime:
    return today_noon - timedelta(days=today_noon.weekday())


@pytest.fixture
def tuesday(monday: datetime) -> datetime:
    return monday + timedelta(days=1)


@pytest.fixture
def wednesday(monday: datetime) -> datetime:
    return monday + timedelta(days=2)


@pytest.fixture
def thursday(monday: datetime) -> datetime:
    return monday + timedelta(days=3)


@pytest.fixture
def friday(monday: datetime) -> datetime:
    return monday + timedelta(days=4)


@pytest.fixture
def saturday(monday: datetime) -> datetime:
    return monday + timedelta(days=5)


@pytest.fixture
def sunday(monday: datetime) -> datetime:
    return monday + timedelta(days=6)


@pytest.fixture
def days(monday: datetime, tuesday: datetime, wednesday: datetime, thursday: datetime,
         friday: datetime, saturday: datetime, sunday: datetime) -> List[datetime]:
    return [monday, tuesday, wednesday, thursday, friday, saturday, sunday]
