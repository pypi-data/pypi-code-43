from clustaar.schemas.v1 import GOOGLE_CUSTOM_SEARCH_ACTION
from clustaar.schemas.models import GoogleCustomSearchAction
import pytest


@pytest.fixture
def action():
    return GoogleCustomSearchAction(query="Tintin", limit=1, custom_engine_id="AZERTY")


@pytest.fixture
def data():
    return {
        "type": "google_custom_search_action",
        "query": "Tintin",
        "limit": 1,
        "customEngineID": "AZERTY",
    }


class TestDump(object):
    def test_returns_a_dict(self, action, data, mapper):
        result = GOOGLE_CUSTOM_SEARCH_ACTION.dump(action, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_an_action(self, data, mapper):
        action = mapper.load(data, GOOGLE_CUSTOM_SEARCH_ACTION)
        assert isinstance(action, GoogleCustomSearchAction)
        assert action.query == "Tintin"
        assert action.custom_engine_id == "AZERTY"
        assert action.limit == 1
