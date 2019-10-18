import pytest
from clustaar.schemas.models import Image
from tests.utils import MAPPER


@pytest.fixture
def image():
    return Image(url="http://example.com/")


@pytest.fixture
def data():
    return {"type": "image", "url": "http://example.com/"}


class TestDump(object):
    def test_returns_a_dict(self, data, image):
        result = MAPPER.dump(image, "image")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "image")
        assert isinstance(result, Image)
        assert result.url == "http://example.com/"
