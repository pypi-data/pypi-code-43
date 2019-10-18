import pytest
from clustaar.schemas.models import Video
from tests.utils import MAPPER


@pytest.fixture
def video():
    return Video(url="http://example.com/")


@pytest.fixture
def data():
    return {"type": "video", "url": "http://example.com/"}


class TestDump(object):
    def test_returns_a_dict(self, data, video):
        result = MAPPER.dump(video, "video")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "video")
        assert isinstance(result, Video)
        assert result.url == "http://example.com/"
