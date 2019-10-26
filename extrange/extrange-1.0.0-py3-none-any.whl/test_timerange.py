from datetime import time
import pytest

from .timerange import TimeRange


@pytest.mark.parametrize('begin,end,valid', (
    (time(), time(), True),
    (None, None, True),
    (time(), None, True),
    (None, time(), True),
    ('a', True, False),
    (0, time(), False),
    (time(), 0, False),
))
def test_constructor_type_check(begin, end, valid):
    if valid:
        TimeRange(begin, end)
    else:
        with pytest.raises(TypeError):
            TimeRange(begin, end)

def test_contains_invalid_value():
    with pytest.raises(TypeError):
        0 in TimeRange(None, None)

@pytest.mark.parametrize('r,v,valid', (
    (TimeRange(time(), time()), time(), False),
    (TimeRange(time(), time(0, 0, 0, 1)), time(), True),
    (TimeRange(time(), time(0, 0, 0, 1)), time(0, 0, 0, 1), False),
    (TimeRange(None, None), time.min, True),
    (TimeRange(None, None), time.max, True),
    (TimeRange(None, time(0, 0, 0, 1)), time.min, True),
    (TimeRange(time.max, None), time.max, True),
    (TimeRange(time(10), time(20)), time(10), True),
    (TimeRange(time(10), time(20)), time(20), False),
    (TimeRange(time(10), time(20)), time(15), True,),
    (TimeRange(time(20), time(10)), time.max, True),
    (TimeRange(time(20), time(10)), time(15), False),
    (TimeRange(time(20), time(10)), time.min, True),
))
def test_contains(r, v, valid):
    if valid:
        assert v in r
    else:
        assert not (v in r)
