import uuid

import pytest

from bluejay.event import ProductSelected


@pytest.fixture
def app_id():
    return str(uuid.uuid4())


@pytest.fixture
def occurred_on(faker):
    return faker.date_time()


@pytest.fixture
def product_id(faker):
    return str(faker.pyint())


@pytest.fixture
def product_name(faker):
    return faker.pystr()


@pytest.fixture
def product_lender_name(faker):
    return faker.pystr()


@pytest.fixture
def event(app_id, occurred_on, product_id, product_name, product_lender_name):
    return ProductSelected(
        app_id=app_id,
        occurred_on=occurred_on,
        product_id=product_id,
        product_name=product_name,
        product_lender_name=product_lender_name,
    )


@pytest.fixture
def event_dict(app_id, occurred_on, product_id, product_name, product_lender_name):
    return dict(
        app_id=app_id,
        occurred_on=occurred_on,
        product_id=product_id,
        product_name=product_name,
        product_lender_name=product_lender_name,
    )


def test_object_is_turned_into_a_dictionary(event, event_dict):
    assert event_dict == event.as_dict()


def test_event_name_is_set_for_bluejay_receiver(event):
    assert "product_selected" == event.event_name
