from clustaar.schemas.v1 import SEND_IMAGE_ACTION
from clustaar.schemas.models import SendImageAction
from lupin.errors import InvalidDocument, InvalidURL

import pytest


@pytest.fixture
def action():
    return SendImageAction(image_url="http://example.com/logo.png")


@pytest.fixture
def data():
    return {"type": "send_image_action", "imageURL": "http://example.com/logo.png"}


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = SEND_IMAGE_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, SEND_IMAGE_ACTION)
        assert isinstance(action, SendImageAction)
        assert action.image_url == "http://example.com/logo.png"


class TestValidate(object):
    def test_do_not_raise_error_if_valid(self, data, mapper):
        mapper.validate(data, SEND_IMAGE_ACTION)

    def test_must_raise_error_if_empty_string(self, data, mapper):
        data["imageURL"] = ""

        with pytest.raises(InvalidDocument) as exc:
            mapper.validate(data, SEND_IMAGE_ACTION)

        errors = exc.value.errors
        assert len(errors) == 1
        error = errors[0]

        assert isinstance(error, InvalidURL)
        assert error.path == ["imageURL"]
