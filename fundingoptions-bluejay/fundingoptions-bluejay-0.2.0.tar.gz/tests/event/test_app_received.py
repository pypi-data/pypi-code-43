import uuid

import pytest

from bluejay.event import AppReceived


@pytest.fixture
def app_id():
    return str(uuid.uuid4())


@pytest.fixture
def occurred_on(faker):
    return faker.date_time()


@pytest.fixture
def event(app_id, occurred_on):
    return AppReceived(app_id=app_id, occurred_on=occurred_on)


@pytest.fixture
def event_dict(app_id, occurred_on):
    return {"app_id": app_id, "occurred_on": occurred_on}


def test_object_is_turned_into_a_dictionary(event, event_dict):
    assert event_dict == event.as_dict()


def test_event_name_is_set_for_bluejay_receiver(event):
    assert "application_received" == event.event_name
