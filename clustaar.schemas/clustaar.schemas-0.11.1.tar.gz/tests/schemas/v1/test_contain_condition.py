from clustaar.schemas.v1 import CONTAIN_CONDITION
from clustaar.schemas.models import ContainCondition
import pytest


@pytest.fixture
def data():
    return {"type": "contains", "values": ["hello", "hi"]}


@pytest.fixture
def condition():
    return ContainCondition(values=["hello", "hi"])


class TestLoad(object):
    def test_must_return_a_condition(self, data, mapper):
        result = mapper.load(data, CONTAIN_CONDITION)
        assert isinstance(result, ContainCondition)
        assert result.values == ["hello", "hi"]


class TestDump(object):
    def test_returns_a_dict(self, condition, data, mapper):
        result = mapper.dump(condition, CONTAIN_CONDITION)
        assert result == data
