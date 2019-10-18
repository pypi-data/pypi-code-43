import pytest
from clustaar.schemas.models import Interlocutor, Coordinates
from tests.utils import MAPPER


@pytest.fixture
def interlocutor():
    return Interlocutor(
        id="123",
        location=Coordinates(lat=1, long=2),
        email="tintin@moulinsart.fr",
        first_name="tintin",
        last_name=None,
        phone_number="0645592034",
        custom_attributes={"age": "21"},
    )


@pytest.fixture
def data():
    return {
        "id": "123",
        "location": {"lat": 1, "long": 2},
        "email": "tintin@moulinsart.fr",
        "firstName": "tintin",
        "lastName": None,
        "phoneNumber": "0645592034",
        "customAttributes": {"age": "21"},
    }


@pytest.fixture
def malicious_data():
    return {
        "id": "123",
        "location": {"lat": 1, "long": 2},
        "email": "tintin@moulinsart.fr",
        "firstName": "<script>void();</script>tintin",
        "lastName": None,
        "phoneNumber": "0645592034",
        "customAttributes": {"age": "21"},
    }


class TestDump(object):
    def test_returns_a_dict(self, data, interlocutor):
        result = MAPPER.dump(interlocutor, "webhook_interlocutor")
        assert result == data


class TestLoad(object):
    def test_returns_an_object(self, data):
        result = MAPPER.load(data, "webhook_interlocutor")
        assert isinstance(result, Interlocutor)
        assert result.id == "123"
        assert result.location.lat == 1
        assert result.location.long == 2
        assert result.email == "tintin@moulinsart.fr"
        assert result.first_name == "tintin"
        assert result.last_name is None
        assert result.custom_attributes == {"age": "21"}
        assert result.phone_number == "0645592034"

    def test_returns_an_object_malicious(self, malicious_data):
        result = MAPPER.load(malicious_data, "webhook_interlocutor")
        assert isinstance(result, Interlocutor)
        assert result.email == "tintin@moulinsart.fr"
        assert result.first_name == "&lt;script&gt;void();&lt;/script&gt;tintin"
