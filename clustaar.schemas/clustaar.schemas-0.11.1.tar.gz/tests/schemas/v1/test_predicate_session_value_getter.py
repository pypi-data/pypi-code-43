from clustaar.schemas.v1 import PREDICATE_SESSION_VALUE_GETTER
from clustaar.schemas.models import SessionValueGetter
import pytest


@pytest.fixture
def data():
    return {"type": "session_value", "key": "name"}


@pytest.fixture
def getter():
    return SessionValueGetter(key="name")


class TestLoad(object):
    def test_must_return_a_getter(self, data, mapper):
        result = mapper.load(data, PREDICATE_SESSION_VALUE_GETTER)
        assert isinstance(result, SessionValueGetter)
        assert result.key == "name"


class TestDump(object):
    def test_returns_a_dict(self, getter, data, mapper):
        result = mapper.dump(getter, PREDICATE_SESSION_VALUE_GETTER)
        assert result == data
