from clustaar.schemas.v1 import STEP_TARGET
from clustaar.schemas.models import StepTarget
from lupin.errors import InvalidDocument, InvalidMatch
import pytest


@pytest.fixture
def target():
    return StepTarget(name="a step", step_id="a1" * 12)


@pytest.fixture
def data():
    return {"type": "step", "name": "a step", "id": "a1" * 12}


class TestDump(object):
    def test_returns_a_dict(self, target, data, mapper):
        result = STEP_TARGET.dump(target, mapper)
        assert result == data


class TestLoad(object):
    def test_returns_a_target(self, data, mapper):
        target = mapper.load(data, STEP_TARGET)
        assert isinstance(target, StepTarget)
        assert target.step_id == "a1" * 12
        assert target.name == "a step"


class TestValidate(object):
    def test_does_nothing_if_ok(self, data, mapper):
        mapper.validate(data, STEP_TARGET)

    def test_raise_error_if_invalid_id(self, data, mapper):
        data["id"] = "az"
        with pytest.raises(InvalidDocument) as exc:
            mapper.validate(data, STEP_TARGET)

        errors = exc.value.errors
        assert len(errors) == 1
        error = errors[0]

        assert isinstance(error, InvalidMatch)
        assert error.path == ["id"]
