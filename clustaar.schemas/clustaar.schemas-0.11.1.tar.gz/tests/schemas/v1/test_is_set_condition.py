from clustaar.schemas.v1 import IS_SET_CONDITION
from clustaar.schemas.models import IsSetCondition
import pytest


@pytest.fixture
def data():
    return {"type": "is_set"}


@pytest.fixture
def condition():
    return IsSetCondition()


class TestLoad(object):
    def test_must_return_a_condition(self, data, mapper):
        result = mapper.load(data, IS_SET_CONDITION)
        assert isinstance(result, IsSetCondition)


class TestDump(object):
    def test_returns_a_dict(self, condition, data, mapper):
        result = mapper.dump(condition, IS_SET_CONDITION)
        assert result == data
