from datetime import time
import pytest

from .range import Range


@pytest.mark.parametrize('r,v,valid', (
    (Range(0, 0), 0, False),
    (Range(0, 1), 0, True),
    (Range(0, 1), 1, False),
    (Range(0, 1), 0.5, True),
    (Range(0, -1), 0, False),
))
def test_contains(r, v, valid):
    if valid:
        assert v in r
    else:
        assert not (v in r)
