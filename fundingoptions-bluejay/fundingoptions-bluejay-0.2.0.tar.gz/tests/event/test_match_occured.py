import uuid

import pytest

from bluejay.event import MatchOccurred


@pytest.fixture
def app_id():
    return str(uuid.uuid4())


@pytest.fixture
def occurred_on(faker):
    return faker.date_time()


@pytest.fixture
def input_data(faker):
    return faker.pydict()


@pytest.fixture
def build_match(faker):
    def inner():
        criteria_names = faker.pylist(3, True, "str")
        return {
            "score": faker.pyint(),
            "breakdown": {name: faker.pyint() for name in criteria_names},
            "criteria": {name: faker.pydict(3, True, "int") for name in criteria_names},
            "product_id": str(faker.pyint()),
            "product_name": faker.pystr(),
            "product_lender_name": faker.pystr(),
        }

    return inner


@pytest.fixture
def matches(faker, build_match):
    return [build_match(), build_match()]


@pytest.fixture
def event(app_id, occurred_on, input_data, matches):
    return MatchOccurred(
        app_id=app_id, occurred_on=occurred_on, input=input_data, matches=matches
    )


@pytest.fixture
def event_dict(app_id, occurred_on, input_data, matches):
    return {
        "app_id": app_id,
        "occurred_on": occurred_on,
        "input": input_data,
        "matches": matches,
    }


def test_object_is_turned_into_a_dictionary(event, event_dict):
    assert event_dict == event.as_dict()


def test_event_name_is_set_for_bluejay_receiver(event):
    assert "match_occurred" == event.event_name
