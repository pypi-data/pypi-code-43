import pytest
from clustaar.schemas.models import Audio
from tests.utils import MAPPER


@pytest.fixture
def audio():
    return Audio(url="http://example.com/")


@pytest.fixture
def data():
    return {"type": "audio", "url": "http://example.com/"}


class TestDump(object):
    def test_returns_a_dict(self, data, audio):
        result = MAPPER.dump(audio, "audio")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "audio")
        assert isinstance(result, Audio)
        assert result.url == "http://example.com/"
