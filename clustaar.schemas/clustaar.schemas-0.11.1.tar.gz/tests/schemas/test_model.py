from clustaar.schemas.models import model
import pytest


@pytest.fixture
def User():
    return model("User", "id")


class TestModel(object):
    def test_raise_error_if_invalid_constructor_parameter(self, User):
        with pytest.raises(TypeError):
            User(name="Tintin")
