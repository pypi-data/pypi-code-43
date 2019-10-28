import pytest

from bluejay.backend.command import SendEvent

_expected_value_types = ["str", "int", "float", "date_time", "dict", "list"]


@pytest.fixture
def event_name(faker):
    return faker.pystr()


@pytest.fixture
def event_payload(faker):
    return faker.pydict(10, True, *_expected_value_types)


@pytest.fixture
def send_event_command(event_name, event_payload):
    return SendEvent(payload=event_payload, event_name=event_name)
