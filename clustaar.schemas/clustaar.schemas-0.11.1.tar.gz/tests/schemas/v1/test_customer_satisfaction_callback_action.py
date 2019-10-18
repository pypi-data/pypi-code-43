import pytest
from clustaar.schemas.models import CustomerSatisfactionCallbackAction, StepTarget
from tests.utils import MAPPER


@pytest.fixture
def callback():
    return CustomerSatisfactionCallbackAction(
        kind="positive", target=StepTarget(step_id="a1" * 12, name="a step")
    )


@pytest.fixture
def data():
    return {
        "type": "customer_satisfaction_callback_action",
        "kind": "positive",
        "target": {"type": "step", "id": "a1" * 12, "name": "a step"},
    }


class TestDump(object):
    def test_returns_a_dict(self, data, callback):
        result = MAPPER.dump(callback, "customer_satisfaction_callback_action")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "customer_satisfaction_callback_action")
        assert isinstance(result, CustomerSatisfactionCallbackAction)
        assert result.kind == "positive"
        assert isinstance(result.target, StepTarget)
        assert result.target.step_id == "a1" * 12
