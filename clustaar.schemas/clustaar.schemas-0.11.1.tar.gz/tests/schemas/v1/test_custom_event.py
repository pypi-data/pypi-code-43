import pytest
from clustaar.schemas.models import CustomEvent
from tests.utils import MAPPER


@pytest.fixture
def event():
    return CustomEvent(name="event1")


@pytest.fixture
def data():
    return {"type": "custom_event", "name": "event1"}


class TestDump(object):
    def test_returns_a_dict(self, data, event):
        result = MAPPER.dump(event, "custom_event")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "custom_event")
        assert isinstance(result, CustomEvent)
        assert result.name == "event1"
