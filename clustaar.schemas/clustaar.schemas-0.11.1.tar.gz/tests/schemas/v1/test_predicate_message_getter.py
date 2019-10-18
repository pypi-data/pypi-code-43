from clustaar.schemas.v1 import PREDICATE_MESSAGE_GETTER
from clustaar.schemas.models import MessageGetter
import pytest


@pytest.fixture
def getter():
    return MessageGetter()


@pytest.fixture
def data():
    return {"type": "message"}


class TestLoad(object):
    def test_must_return_a_getter(self, data, mapper):
        result = mapper.load(data, PREDICATE_MESSAGE_GETTER)
        assert isinstance(result, MessageGetter)


class TestDump(object):
    def test_returns_a_dict(self, getter, data, mapper):
        result = mapper.dump(getter, PREDICATE_MESSAGE_GETTER)
        assert result == data
