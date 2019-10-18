from clustaar.schemas.v1 import FLOW_CONNECTION_PREDICATE
from clustaar.schemas.models import ConnectionPredicate, IsSetCondition, MessageGetter
import pytest


@pytest.fixture
def data():
    return {
        "type": "connection_predicate",
        "condition": {"type": "is_set"},
        "valueGetter": {"type": "message"},
    }


@pytest.fixture
def predicate():
    return ConnectionPredicate(condition=IsSetCondition(), value_getter=MessageGetter())


class TestLoad(object):
    def test_returns_a_predicate(self, data, mapper):
        result = mapper.load(data, FLOW_CONNECTION_PREDICATE)
        assert isinstance(result, ConnectionPredicate)
        assert isinstance(result.condition, IsSetCondition)
        assert isinstance(result.value_getter, MessageGetter)


class TestDump(object):
    def test_returns_a_dict(self, data, mapper, predicate):
        result = mapper.dump(predicate, FLOW_CONNECTION_PREDICATE)
        assert result == data
