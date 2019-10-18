from clustaar.schemas.v1 import SET_USER_ATTRIBUTE_ACTION
from clustaar.schemas.models import SetUserAttributeAction
from lupin.errors import InvalidDocument, InvalidMatch
import pytest


@pytest.fixture
def action():
    return SetUserAttributeAction(key="var1", value="val1")


@pytest.fixture
def data():
    return {"type": "set_user_attribute_action", "key": "var1", "value": "val1"}


@pytest.fixture
def malicious_data():
    return {
        "type": "set_user_attribute_action",
        "key": "var1",
        "value": "<script>void();</script>val1",
    }


class TestDump:
    def test_returns_a_dict(self, action, data, mapper):
        result = SET_USER_ATTRIBUTE_ACTION.dump(action, mapper)
        assert result == data


class TestLoad:
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SET_USER_ATTRIBUTE_ACTION)
        assert isinstance(action, SetUserAttributeAction)
        assert action.key == "var1"
        assert action.value == "val1"

    def test_returns_an_action_malicious(self, malicious_data, mapper):
        action = mapper.load(malicious_data, SET_USER_ATTRIBUTE_ACTION)
        assert isinstance(action, SetUserAttributeAction)
        assert action.key == "var1"
        assert action.value == "&lt;script&gt;void();&lt;/script&gt;val1"


class TestValidate:
    def test_does_nothing_if_ok(self, data, mapper):
        mapper.validate(data, SET_USER_ATTRIBUTE_ACTION)

    @pytest.mark.parametrize("key", ["id", "Id", "iD", "ID"])
    def test_raise_error_if_key_is_invalid(self, data, mapper, key):
        data["key"] = key
        with pytest.raises(InvalidDocument) as exc:
            mapper.validate(data, SET_USER_ATTRIBUTE_ACTION)

        errors = exc.value.errors
        assert len(errors) == 1
        error = errors[0]

        assert isinstance(error, InvalidMatch)
        assert error.path == ["key"]
