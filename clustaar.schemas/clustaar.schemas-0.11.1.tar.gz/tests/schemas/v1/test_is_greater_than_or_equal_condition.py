from clustaar.schemas.v1 import IS_GREATER_THAN_OR_EQUAL_CONDITION
from clustaar.schemas.models import IsGreaterThanOrEqualCondition
import pytest


@pytest.fixture
def condition():
    return IsGreaterThanOrEqualCondition(minimum=10)


@pytest.fixture
def data():
    return {"type": "is_greater_than_or_equal", "minimum": 10}


class TestDump(object):
    def test_returns_data(self, condition, data, mapper):
        result = mapper.dump(condition)
        assert data == result


class TestLoad(object):
    def test_returns_a_condition(self, condition, data, mapper):
        condition = mapper.load(data, IS_GREATER_THAN_OR_EQUAL_CONDITION)
        assert isinstance(condition, IsGreaterThanOrEqualCondition)
        assert condition.minimum == 10
