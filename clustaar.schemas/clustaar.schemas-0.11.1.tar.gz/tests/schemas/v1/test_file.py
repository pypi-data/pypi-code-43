import pytest
from clustaar.schemas.models import File
from tests.utils import MAPPER


@pytest.fixture
def file():
    return File(url="http://example.com/")


@pytest.fixture
def data():
    return {"type": "file", "url": "http://example.com/"}


class TestDump(object):
    def test_returns_a_dict(self, data, file):
        result = MAPPER.dump(file, "file")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "file")
        assert isinstance(result, File)
        assert result.url == "http://example.com/"
