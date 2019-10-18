from clustaar.schemas.v1 import SEND_EMAIL_ACTION
from clustaar.schemas.models import SendEmailAction
from lupin.errors import InvalidDocument, InvalidMatch

import pytest


@pytest.fixture
def action():
    return SendEmailAction(
        from_email="tintin@gmail.com",
        from_name="Tintin",
        recipient="test@example.com",
        subject="Hello",
        content=":)",
    )


@pytest.fixture
def data():
    return {
        "type": "send_email_action",
        "fromEmail": "tintin@gmail.com",
        "fromName": "Tintin",
        "recipient": "test@example.com",
        "subject": "Hello",
        "content": ":)",
    }


@pytest.fixture
def malicious_data():
    return {
        "type": "send_email_action",
        "fromEmail": "tintin@gmail.com",
        "fromName": "Tintin",
        "recipient": "test@example.com",
        "subject": "Hello",
        "content": "<script>void();</script>:)",
    }


class TestDump:
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_EMAIL_ACTION.dump(action, mapper)
        assert result == data


class TestLoad:
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_EMAIL_ACTION)
        assert isinstance(action, SendEmailAction)
        assert action.content == ":)"
        assert action.subject == "Hello"
        assert action.recipient == "test@example.com"
        assert action.from_email == "tintin@gmail.com"
        assert action.from_name == "Tintin"

    def test_returns_an_action_malicious(self, malicious_data, mapper):
        action = mapper.load(malicious_data, SEND_EMAIL_ACTION)
        assert isinstance(action, SendEmailAction)
        assert action.content == "&lt;script&gt;void();&lt;/script&gt;:)"
        assert action.subject == "Hello"
        assert action.recipient == "test@example.com"
        assert action.from_email == "tintin@gmail.com"
        assert action.from_name == "Tintin"


class TestValidate:
    def test_raises_if_from_email_contains_clustaar_domain(self, data, mapper):
        data["fromEmail"] = "titin@clustaar.com"

        with pytest.raises(InvalidDocument):
            mapper.validate(data, SEND_EMAIL_ACTION)

        data["fromEmail"] = "titin@CluStaaR.com"

        with pytest.raises(InvalidDocument):
            mapper.validate(data, SEND_EMAIL_ACTION)

    def test_do_not_raises_if_from_email_doesnt_contains_clustaar_domain(self, data, mapper):
        data["fromEmail"] = "titin@clustaaar.com"
        mapper.validate(data, SEND_EMAIL_ACTION)

        data["fromEmail"] = "titin@gmail.com"
        mapper.validate(data, SEND_EMAIL_ACTION)

    def test_do_not_raise_error_if_from_email_is_empty(self, data, mapper):
        data["fromEmail"] = ""
        data["fromName"] = ""
        mapper.validate(data, SEND_EMAIL_ACTION)
