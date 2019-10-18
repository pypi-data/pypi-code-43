from clustaar.schemas.v1 import SEND_WEBHOOK_REQUEST_ACTION
from clustaar.schemas.models import SendWebhookRequestAction, WebhookRequestField
import pytest


@pytest.fixture
def fields():
    return [WebhookRequestField(key="name", value="Tintin")]


@pytest.fixture
def action(fields):
    return SendWebhookRequestAction(
        url="www.zapier.com", service="zapier", description="Je suis là!", fields=fields
    )


@pytest.fixture
def data():
    return {
        "type": "send_webhook_request_action",
        "url": "www.zapier.com",
        "service": "zapier",
        "description": "Je suis là!",
        "fields": [{"type": "webhook_request_field", "key": "name", "value": "Tintin"}],
    }


class TestDump:
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_WEBHOOK_REQUEST_ACTION.dump(action, mapper)
        assert result == data


class TestLoad:
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_WEBHOOK_REQUEST_ACTION)
        assert isinstance(action, SendWebhookRequestAction)
        assert action.url == "www.zapier.com"
        assert action.service == "zapier"
        assert action.description == "Je suis là!"
        assert action.fields[0].key == "name"
        assert action.fields[0].value == "Tintin"


class TestValidate(object):
    def test_do_not_raise(self, action, data, mapper):
        mapper.validate(data, SEND_WEBHOOK_REQUEST_ACTION)
