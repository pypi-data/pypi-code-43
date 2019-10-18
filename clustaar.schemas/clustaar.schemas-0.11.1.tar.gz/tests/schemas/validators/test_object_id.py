from clustaar.schemas.validators import ObjectID
from lupin.errors import InvalidMatch
import pytest


@pytest.fixture
def validator():
    return ObjectID()


class TestCall(object):
    def test_raise_error_if_invalid_oid(self, validator):
        with pytest.raises(InvalidMatch):
            validator("", [])

    def test_does_not_raise_error_if_valid_oid(self, validator):
        validator("a1" * 12, [])
