from clustaar.schemas.validators import IsRegexp
from lupin.errors import ValidationError
import pytest


@pytest.fixture
def validator():
    return IsRegexp()


class TestCall(object):
    def test_do_not_raise_error_if_valid_regex(self, validator):
        validator(r"\d", [])

    def test_raise_error_if_invalid_regex(self, validator):
        with pytest.raises(ValidationError):
            validator("(\d", [])
