import pytest

from clustaar.schemas.v1 import ASSIGN_INTERCOM_CONVERSATION_ACTION
from clustaar.schemas.models import AssignIntercomConversationAction
from lupin.errors import InvalidDocument, InvalidMatch


@pytest.fixture
def action():
    return AssignIntercomConversationAction(assignee_id="1234567")


@pytest.fixture
def data():
    return {"type": "assign_intercom_conversation_action", "assigneeID": "1234567"}


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = ASSIGN_INTERCOM_CONVERSATION_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, ASSIGN_INTERCOM_CONVERSATION_ACTION)
        assert isinstance(action, AssignIntercomConversationAction)
        assert action.assignee_id == "1234567"


class TestValidate(object):
    def test_does_nothing_if_ok(self, data, mapper):
        mapper.validate(data, ASSIGN_INTERCOM_CONVERSATION_ACTION)

    def test_does_nothing_if_assignee_id_is_blank(self, data, mapper):
        data["assigneeID"] = ""
        mapper.validate(data, ASSIGN_INTERCOM_CONVERSATION_ACTION)

    def test_does_nothing_if_assignee_id_is_none(self, data, mapper):
        data["assigneeID"] = None
        mapper.validate(data, ASSIGN_INTERCOM_CONVERSATION_ACTION)

    def test_does_nothing_if_assignee_id_is_not_present(self, data, mapper):
        del data["assigneeID"]
        mapper.validate(data, ASSIGN_INTERCOM_CONVERSATION_ACTION)

    def test_raise_error_if_assignee_id_have_invalid_format(self, data, mapper):
        data["assigneeID"] = "toto3"

        with pytest.raises(InvalidDocument) as exc:
            mapper.validate(data, ASSIGN_INTERCOM_CONVERSATION_ACTION)

        errors = exc.value.errors
        error = errors[0]

        assert error.path == ["assigneeID"]
        assert len(errors) == 1
        assert isinstance(error, InvalidMatch)
