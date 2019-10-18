from clustaar.schemas.v1 import EQUALS_CONDITION
from clustaar.schemas.models import EqualsCondition
import pytest


@pytest.fixture
def data():
    return {"type": "equals", "expected": "hello"}


@pytest.fixture
def condition():
    return EqualsCondition(expected="hello")


class TestLoad(object):
    def test_must_return_a_condition(self, data, mapper):
        result = mapper.load(data, EQUALS_CONDITION)
        assert isinstance(result, EqualsCondition)
        assert result.expected == "hello"


class TestDump(object):
    def test_returns_a_dict(self, condition, data, mapper):
        result = mapper.dump(condition, EQUALS_CONDITION)
        assert result == data
