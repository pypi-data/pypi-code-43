import pytest
from clustaar.schemas.v1 import LEGACY_REPLY_TO_MESSAGE_ACTION
from clustaar.schemas.models import LegacyReplyToMessageAction


@pytest.fixture
def action():
    return LegacyReplyToMessageAction(message="ok")


@pytest.fixture
def malicious_action():
    return LegacyReplyToMessageAction(message="<script>void();</script>ok")


@pytest.fixture
def data(action):
    return {"type": "legacy_reply_to_message_action", "message": action.message}


@pytest.fixture
def malicious_data(malicious_action):
    return {"type": "legacy_reply_to_message_action", "message": malicious_action.message}


@pytest.fixture
def sanitized():
    return "&lt;script&gt;void();&lt;/script&gt;ok"


class TestLoad:
    def test_loads_an_action(self, action, data, mapper):
        loaded_action = mapper.load(data, LEGACY_REPLY_TO_MESSAGE_ACTION)
        assert loaded_action.message == action.message


class TestLoadMalicious:
    def test_loads_an_action(self, action, malicious_data, mapper, sanitized):
        loaded_action = mapper.load(malicious_data, LEGACY_REPLY_TO_MESSAGE_ACTION)
        assert loaded_action.message == sanitized


class TestDump:
    def test_dump_targs_into_dict(self, action, data, mapper):
        dump = LEGACY_REPLY_TO_MESSAGE_ACTION.dump(action, mapper)
        assert dump == data
