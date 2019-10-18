import pytest
from clustaar.schemas.models import URLLoadedEvent
from tests.utils import MAPPER


@pytest.fixture
def event():
    return URLLoadedEvent(url="http://example.com/")


@pytest.fixture
def data():
    return {"type": "url_loaded_event", "url": "http://example.com/"}


class TestDump(object):
    def test_returns_a_dict(self, data, event):
        result = MAPPER.dump(event, "url_loaded_event")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "url_loaded_event")
        assert isinstance(result, URLLoadedEvent)
        assert result.url == "http://example.com/"
