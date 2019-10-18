from clustaar.schemas.v1 import SEND_TEXT_ACTION
from clustaar.schemas.models import SendTextAction
import pytest


@pytest.fixture
def action():
    return SendTextAction(alternatives=["Hi", "Hello"], text="Hello")


@pytest.fixture
def action2():
    return SendTextAction(alternatives=["Hi", "Hello"])


@pytest.fixture
def data():
    return {"type": "send_text_action", "alternatives": ["Hi", "Hello"], "text": "Hello"}


@pytest.fixture
def data2():
    return {"type": "send_text_action", "alternatives": ["Hi", "Hello"]}


@pytest.fixture
def ampersand_data():
    return {"type": "send_text_action", "alternatives": ["Hi", "Hello & How Are You?"]}


@pytest.fixture
def br_data():
    return {"type": "send_text_action", "alternatives": ["Hi<br>", "Hello & <br />How Are You?"]}


@pytest.fixture
def re_data():
    return {
        "type": "send_text_action",
        "alternatives": ["Hi(?P\d{5})", "Hello & (?P\d{5})How Are You?"],
    }


@pytest.fixture
def malicious_data():
    return {"type": "send_text_action", "alternatives": ["<script>void();</script>Hi", "Hello"]}


class TestDump:
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_TEXT_ACTION.dump(action, mapper)
        assert result == data

    def test_does_not_return_null_text(self, action2, data2, mapper):
        result = SEND_TEXT_ACTION.dump(action2, mapper)
        assert result == data2


class TestLoad:
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_TEXT_ACTION)
        assert isinstance(action, SendTextAction)
        assert action.alternatives == ["Hi", "Hello"]

    def test_fail_load_text(self, data, mapper):
        action = mapper.load(data, SEND_TEXT_ACTION)
        assert action.text is None

    def test_preserve_ampersand(self, ampersand_data, mapper):
        action = mapper.load(ampersand_data, SEND_TEXT_ACTION)
        assert action.alternatives == ["Hi", "Hello & How Are You?"]

    def test_preserve_br(self, br_data, mapper):
        action = mapper.load(br_data, SEND_TEXT_ACTION)
        assert action.alternatives == ["Hi<br>", "Hello & <br>How Are You?"]

    def test_preserve_regex(self, re_data, mapper):
        action = mapper.load(re_data, SEND_TEXT_ACTION)
        assert action.alternatives == ["Hi(?P\d{5})", "Hello & (?P\d{5})How Are You?"]

    def test_returns_an_action_malicious(self, malicious_data, mapper):
        send_text = mapper.load(malicious_data, SEND_TEXT_ACTION)
        assert isinstance(send_text, SendTextAction)
        assert send_text.alternatives == ["&lt;script&gt;void();&lt;/script&gt;Hi", "Hello"]
