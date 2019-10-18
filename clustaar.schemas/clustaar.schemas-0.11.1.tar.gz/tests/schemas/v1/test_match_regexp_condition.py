import re
from clustaar.schemas.v1 import MATCH_REGEXP_CONDITION
from clustaar.schemas.models import MatchRegexpCondition
import pytest


@pytest.fixture
def data():
    return {"type": "match_regexp", "pattern": "(hello)"}


@pytest.fixture
def condition():
    return MatchRegexpCondition(regexp=re.compile("(hello)"))


class TestLoad(object):
    def test_must_return_a_condition(self, data, mapper):
        result = mapper.load(data, MATCH_REGEXP_CONDITION)
        assert isinstance(result, MatchRegexpCondition)
        assert result.regexp == re.compile("(hello)")


class TestDump(object):
    def test_returns_a_dict(self, condition, data, mapper):
        result = mapper.dump(condition, MATCH_REGEXP_CONDITION)
        assert result == data
