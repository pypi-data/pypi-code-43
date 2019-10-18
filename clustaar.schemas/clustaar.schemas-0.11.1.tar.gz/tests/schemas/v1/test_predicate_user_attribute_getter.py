from clustaar.schemas.v1 import PREDICATE_USER_ATTRIBUTE_GETTER
from clustaar.schemas.models import UserAttributeGetter
import pytest


@pytest.fixture
def data():
    return {"type": "user_attribute", "key": "name"}


@pytest.fixture
def getter():
    return UserAttributeGetter(key="name")


class TestLoad(object):
    def test_must_return_a_getter(self, data, mapper):
        result = mapper.load(data, PREDICATE_USER_ATTRIBUTE_GETTER)
        assert isinstance(result, UserAttributeGetter)
        assert result.key == "name"


class TestDump(object):
    def test_returns_a_dict(self, getter, data, mapper):
        result = mapper.dump(getter, PREDICATE_USER_ATTRIBUTE_GETTER)
        assert result == data
