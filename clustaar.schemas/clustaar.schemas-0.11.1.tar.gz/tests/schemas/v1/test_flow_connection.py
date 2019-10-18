from clustaar.schemas.v1 import FLOW_CONNECTION
from clustaar.schemas.models import (
    FlowConnection,
    IsSetCondition,
    MessageGetter,
    StepTarget,
    ConnectionPredicate,
)
import pytest


@pytest.fixture
def data():
    return {
        "type": "flow_connection",
        "target": {"id": "a1" * 12, "type": "step", "name": "a step"},
        "predicates": [
            {
                "type": "connection_predicate",
                "condition": {"type": "is_set"},
                "valueGetter": {"type": "message"},
            }
        ],
    }


@pytest.fixture
def connection():
    predicate = ConnectionPredicate(condition=IsSetCondition(), value_getter=MessageGetter())
    return FlowConnection(
        predicates=[predicate], target=StepTarget(step_id="a1" * 12, name="a step")
    )


class TestLoad(object):
    def test_returns_a_predicate(self, data, mapper):
        result = mapper.load(data, FLOW_CONNECTION)
        assert isinstance(result, FlowConnection)
        target = result.target
        assert isinstance(target, StepTarget)
        assert target.step_id == "a1" * 12
        predicate = result.predicates[0]
        assert isinstance(predicate, ConnectionPredicate)
        assert isinstance(predicate.condition, IsSetCondition)
        assert isinstance(predicate.value_getter, MessageGetter)


class TestDump(object):
    def test_returns_a_dict(self, data, connection, mapper):
        result = mapper.dump(connection, FLOW_CONNECTION)
        assert result == data
