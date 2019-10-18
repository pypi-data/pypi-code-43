import pytest
from clustaar.schemas.models import (
    CustomerSatisfactionAction,
    CustomerSatisfactionChoice,
    StepTarget,
    MatchIntentConditionIntent,
)
from tests.utils import MAPPER


@pytest.fixture
def action():
    choice1 = CustomerSatisfactionChoice(
        kind="positive",
        target=StepTarget(step_id="a1" * 12, name="a step"),
        matching_intent_id="b1" * 12,
        label="yes",
    )
    choice1.matching_intent = MatchIntentConditionIntent(id="b1" * 12, name="an intent")

    choice2 = CustomerSatisfactionChoice(
        kind="negative",
        target=StepTarget(step_id="a2" * 12, name="a step"),
        matching_intent_id="b2" * 12,
        label="no",
    )
    choice2.matching_intent = MatchIntentConditionIntent(id="b2" * 12, name="another intent")

    return CustomerSatisfactionAction(message="Are you satisfied ?", choices=[choice1, choice2])


@pytest.fixture
def data():
    return {
        "type": "customer_satisfaction_action",
        "message": "Are you satisfied ?",
        "choices": [
            {
                "type": "customer_satisfaction_choice",
                "kind": "positive",
                "label": "yes",
                "matchingIntent": {"id": "b1" * 12, "name": "an intent", "type": "intent"},
                "target": {"type": "step", "id": "a1" * 12, "name": "a step"},
            },
            {
                "type": "customer_satisfaction_choice",
                "kind": "negative",
                "matchingIntent": {"id": "b2" * 12, "name": "another intent", "type": "intent"},
                "label": "no",
                "target": {"type": "step", "id": "a2" * 12, "name": "a step"},
            },
        ],
    }


@pytest.fixture
def malicious_data():
    return {
        "type": "customer_satisfaction_action",
        "message": "<script>void();</script>Are you satisfied ?",
        "choices": [
            {
                "type": "customer_satisfaction_choice",
                "kind": "positive",
                "label": "<script>void();</script>yes",
                "matchingIntent": {"id": "b1" * 12, "name": "an intent", "type": "intent"},
                "target": {"type": "step", "id": "a1" * 12, "name": "a step"},
            },
            {
                "type": "customer_satisfaction_choice",
                "kind": "negative",
                "matchingIntent": {"id": "b2" * 12, "name": "another intent", "type": "intent"},
                "label": "no",
                "target": {"type": "step", "id": "a2" * 12, "name": "a step"},
            },
        ],
    }


class TestDump(object):
    def test_returns_a_dict(self, data, action):
        result = MAPPER.dump(action, "customer_satisfaction_action")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "customer_satisfaction_action")
        assert isinstance(result, CustomerSatisfactionAction)
        assert result.message == "Are you satisfied ?"
        assert len(result.choices) == 2

        choice1, choice2 = result.choices
        assert choice1.kind == "positive"
        assert choice1.target.step_id == "a1" * 12
        assert choice1.matching_intent_id == "b1" * 12
        assert choice1.label == "yes"

        assert choice2.kind == "negative"
        assert choice2.target.step_id == "a2" * 12
        assert choice2.matching_intent_id == "b2" * 12
        assert choice2.label == "no"

    def test_returns_an_object_malicious(self, malicious_data):
        result = MAPPER.load(malicious_data, "customer_satisfaction_action")
        assert isinstance(result, CustomerSatisfactionAction)
        assert result.message == "&lt;script&gt;void();&lt;/script&gt;Are you satisfied ?"

        choice1, choice2 = result.choices
        assert choice1.kind == "positive"
        assert choice1.label == "&lt;script&gt;void();&lt;/script&gt;yes"
