from clustaar.schemas.v1 import IS_GREATER_THAN_CONDITION
from clustaar.schemas.models import IsGreaterThanCondition
import pytest


@pytest.fixture
def condition():
    return IsGreaterThanCondition(minimum=10)


@pytest.fixture
def data():
    return {"type": "is_greater_than", "minimum": 10}


class TestDump(object):
    def test_returns_data(self, condition, data, mapper):
        result = mapper.dump(condition)
        assert data == result


class TestLoad(object):
    def test_returns_a_condition(self, condition, data, mapper):
        condition = mapper.load(data, IS_GREATER_THAN_CONDITION)
        assert isinstance(condition, IsGreaterThanCondition)
        assert condition.minimum == 10
