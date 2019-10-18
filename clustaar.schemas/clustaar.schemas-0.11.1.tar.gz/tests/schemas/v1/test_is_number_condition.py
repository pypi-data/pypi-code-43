from clustaar.schemas.v1 import IS_NUMBER_CONDITION
from clustaar.schemas.models import IsNumberCondition
import pytest


@pytest.fixture
def condition():
    return IsNumberCondition()


@pytest.fixture
def data():
    return {"type": "is_number"}


class TestDump(object):
    def test_returns_data(self, condition, data, mapper):
        result = mapper.dump(condition)
        assert data == result


class TestLoad(object):
    def test_returns_a_condition(self, condition, data, mapper):
        condition = mapper.load(data, IS_NUMBER_CONDITION)
        assert isinstance(condition, IsNumberCondition)
