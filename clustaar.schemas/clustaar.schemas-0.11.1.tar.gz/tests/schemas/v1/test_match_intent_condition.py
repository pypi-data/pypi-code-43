from clustaar.schemas.v1 import MATCH_INTENT_CONDITION
from clustaar.schemas.models import MatchIntentCondition, MatchIntentConditionIntent
import pytest


@pytest.fixture
def data():
    return {
        "type": "match_intent",
        "intent": {"type": "intent", "id": "a1" * 12, "name": "an intent"},
    }


@pytest.fixture
def condition():
    condition = MatchIntentCondition(intent_id="a1" * 12)
    condition.intent = MatchIntentConditionIntent(id="a1" * 12, name="an intent")
    return condition


class TestLoad(object):
    def test_must_return_a_condition(self, data, mapper):
        result = mapper.load(data, MATCH_INTENT_CONDITION)
        assert isinstance(result, MatchIntentCondition)
        assert result.intent_id == "a1" * 12


class TestDump(object):
    def test_returns_a_dict(self, condition, data, mapper):
        result = mapper.dump(condition, MATCH_INTENT_CONDITION)
        assert result == data
