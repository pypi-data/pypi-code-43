from clustaar.schemas.v1 import IS_LESS_THAN_CONDITION
from clustaar.schemas.models import IsLessThanCondition
import pytest


@pytest.fixture
def condition():
    return IsLessThanCondition(maximum=10)


@pytest.fixture
def data():
    return {"type": "is_less_than", "maximum": 10}


class TestDump(object):
    def test_returns_data(self, condition, data, mapper):
        result = mapper.dump(condition)
        assert data == result


class TestLoad(object):
    def test_returns_a_condition(self, condition, data, mapper):
        condition = mapper.load(data, IS_LESS_THAN_CONDITION)
        assert isinstance(condition, IsLessThanCondition)
        assert condition.maximum == 10
