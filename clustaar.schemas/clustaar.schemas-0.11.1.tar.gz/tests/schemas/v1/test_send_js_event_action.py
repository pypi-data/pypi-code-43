from clustaar.schemas.v1 import SEND_JS_EVENT_ACTION
from clustaar.schemas.models import SendJSEventAction
import pytest


@pytest.fixture
def action():
    return SendJSEventAction(event="test")


@pytest.fixture
def data():
    return {"type": "send_js_event_action", "event": "test"}


class TestDump:
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_JS_EVENT_ACTION.dump(action, mapper)
        assert result == data


class TestLoad:
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_JS_EVENT_ACTION)
        assert isinstance(action, SendJSEventAction)
        assert action.event == data["event"]
