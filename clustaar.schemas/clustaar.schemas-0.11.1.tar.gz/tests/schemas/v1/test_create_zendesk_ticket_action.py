import pytest

from clustaar.schemas.models import CreateZendeskTicketAction, ZendeskUser
from clustaar.schemas.v1 import CREATE_ZENDESK_TICKET_ACTION
from lupin.errors import InvalidDocument, InvalidLength, NotEqual, InvalidMatch
from clustaar.schemas.constants import (
    ZENDESK_TICKET_TYPES,
    ZENDESK_TICKET_PRIORITIES,
    ZENDESK_TICKET_TAG_MAX_LENGTH,
    ZENDESK_TICKET_TAGS_MAX_COUNT,
    ZENDESK_USER_NAME_MAX_LENGTH,
    ZENDESK_USER_EMAIL_MAX_LENGTH,
    ZENDESK_TICKET_SUBJECT_MAX_LENGTH,
    ZENDESK_TICKET_GROUP_ID_MAX_LENGTH,
    ZENDESK_TICKET_ASSIGNEE_ID_MAX_LENGTH,
    ZENDESK_TICKET_DESCRIPTION_MAX_LENGTH,
)


@pytest.fixture
def action(user):
    return CreateZendeskTicketAction(
        group_id="12" * 12,
        assignee_id="21" * 12,
        subject="Tester cette action",
        description="Pfff aucune idée",
        tags=["finished", "fish", "turtle"],
        ticket_type=list(ZENDESK_TICKET_TYPES)[0],
        ticket_priority=list(ZENDESK_TICKET_PRIORITIES)[0],
        user=ZendeskUser(
            email="Tintin@doe.fifi", name="Je suis un super test", phone_number="0611654852"
        ),
    )


@pytest.fixture
def user():
    return {
        "name": "Je suis un super test",
        "email": "Tintin@doe.fifi",
        "phoneNumber": "0611654852",
    }


@pytest.fixture
def data(user):
    return {
        "ticketPriority": list(ZENDESK_TICKET_PRIORITIES)[0],
        "ticketType": list(ZENDESK_TICKET_TYPES)[0],
        "type": "create_zendesk_ticket_action",
        "tags": ["finished", "fish", "turtle"],
        "description": "Pfff aucune idée",
        "subject": "Tester cette action",
        "assigneeID": "21" * 12,
        "groupID": "12" * 12,
        "user": user,
    }


def assert_raise_on_length(mapper, data):
    with pytest.raises(InvalidDocument) as errors:
        mapper.validate(data, CREATE_ZENDESK_TICKET_ACTION)

    error = errors.value[0]
    assert isinstance(error, InvalidLength)


def assert_raise_on_equal(mapper, data):
    with pytest.raises(InvalidDocument) as errors:
        mapper.validate(data, CREATE_ZENDESK_TICKET_ACTION)

    error = errors.value[0]
    assert isinstance(error, NotEqual)


def assert_raise_on_format(mapper, data):
    with pytest.raises(InvalidDocument) as errors:
        mapper.validate(data, CREATE_ZENDESK_TICKET_ACTION)

    error = errors.value[0]
    assert isinstance(error, InvalidMatch)


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = CREATE_ZENDESK_TICKET_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, CREATE_ZENDESK_TICKET_ACTION)
        assert isinstance(action, CreateZendeskTicketAction)


class TestValidate(object):
    def test_raise_if_dirty_ticket_type(self, mapper, data, user):
        data["ticketType"] = "hh"
        assert_raise_on_equal(mapper, data)

    def test_raise_if_dirty_ticket_priority(self, mapper, data, user):
        data["ticketPriority"] = "hh"
        assert_raise_on_equal(mapper, data)

    def test_raise_if_dirty_name(self, mapper, data, user):
        user["name"] = "a" * (ZENDESK_USER_NAME_MAX_LENGTH + 1)
        assert_raise_on_length(mapper, data)

    def test_raise_if_dirty_email(self, mapper, data, user):
        user["email"] = "a" * (ZENDESK_USER_EMAIL_MAX_LENGTH + 1)
        assert_raise_on_length(mapper, data)

    def test_raise_if_dirty_subject(self, mapper, data):
        data["subject"] = "a" * (ZENDESK_TICKET_SUBJECT_MAX_LENGTH + 1)
        assert_raise_on_length(mapper, data)

    def test_raise_if_dirty_description(self, mapper, data):
        data["description"] = "a" * (ZENDESK_TICKET_DESCRIPTION_MAX_LENGTH + 1)
        assert_raise_on_length(mapper, data)

        data["description"] = ""
        assert_raise_on_length(mapper, data)

    def test_raise_if_dirty_group_id(self, mapper, data):
        data["groupID"] = "1" * (ZENDESK_TICKET_GROUP_ID_MAX_LENGTH + 1)
        assert_raise_on_length(mapper, data)

        data["groupID"] = "1j"
        assert_raise_on_format(mapper, data)

    def test_raise_if_dirty_assignee_id(self, mapper, data):
        data["assigneeID"] = "1" * (ZENDESK_TICKET_ASSIGNEE_ID_MAX_LENGTH + 1)
        assert_raise_on_length(mapper, data)

        data["assigneeID"] = "1j"
        assert_raise_on_format(mapper, data)

    def test_raise_if_dirty_tags(self, mapper, data):
        data["tags"] = [str(n) for n in range((ZENDESK_TICKET_TAGS_MAX_COUNT + 1))]
        assert_raise_on_length(mapper, data)

        data["tags"] = ["a" * (ZENDESK_TICKET_TAG_MAX_LENGTH + 1)]
        assert_raise_on_length(mapper, data)
