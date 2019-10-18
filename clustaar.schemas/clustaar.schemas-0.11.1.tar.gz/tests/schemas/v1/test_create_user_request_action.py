from clustaar.schemas.v1 import CREATE_USER_REQUEST_ACTION
from clustaar.schemas.models import CreateUserRequestAction
import pytest


@pytest.fixture
def action():
    return CreateUserRequestAction(message="I need help", assignee_id="a1" * 12)


@pytest.fixture
def data():
    return {"type": "create_user_request_action", "message": "I need help", "assigneeID": "a1" * 12}


@pytest.fixture
def malicious_data():
    return {
        "type": "create_user_request_action",
        "message": "<script>void();</script>I need help",
        "assigneeID": "a1" * 12,
    }


class TestDump:
    def test_returns_a_dict(self, action, data, mapper):
        result = CREATE_USER_REQUEST_ACTION.dump(action, mapper)
        assert result == data


class TestLoad:
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, CREATE_USER_REQUEST_ACTION)
        assert isinstance(action, CreateUserRequestAction)
        assert action.message == "I need help"
        assert action.assignee_id == "a1" * 12

    def test_returns_an_action_malicious(self, malicious_data, mapper):
        action = mapper.load(malicious_data, CREATE_USER_REQUEST_ACTION)
        assert isinstance(action, CreateUserRequestAction)
        assert action.message == "&lt;script&gt;void();&lt;/script&gt;I need help"


class TestValidate(object):
    def test_do_not_raise(self, action, data, mapper):
        mapper.validate(data, CREATE_USER_REQUEST_ACTION)

        data["assignee_id"] = None
        mapper.validate(data, CREATE_USER_REQUEST_ACTION)

        del data["assignee_id"]
        mapper.validate(data, CREATE_USER_REQUEST_ACTION)
