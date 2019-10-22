import pytest
from slash_step import STEP


def test_step_entry():
    msg = "Some step message"
    with STEP(msg) as step:
        assert isinstance(step, STEP)
        assert str(step) == msg
        assert msg in repr(step)


def test_step_success(called_counters):
    called_counters.verify_calls(start=0, success=0, end=0, error=0)
    with STEP("This will succeed"):
        called_counters.verify_calls(start=1, success=0, end=0, error=0)
    called_counters.verify_calls(start=1, success=1, end=1, error=0)


class CustomError(Exception):
    pass


def test_step_error(called_counters):
    called_counters.verify_calls(start=0, success=0, end=0, error=0)
    with pytest.raises(CustomError):
        with STEP("This will fail"):
            called_counters.verify_calls(start=1, success=0, end=0, error=0)
            raise CustomError('My exception')
    called_counters.verify_calls(start=1, success=0, end=1, error=1)


def test_step_creation_with_arguments():
    step = STEP("Message with args and kwargs", "args", kwargs='kwargs')
    assert step.message, "Message with args and kwargs"


def test_step_creation_with_curly_brackets_with_arguments():
    step = STEP("Message with {} and {kwargs}", "args", kwargs="some_kwargs")
    assert step.message, "Message with args and some_kwargs"


def test_step_creation_with_curly_brackets_without_arguments():
    message = "My message with {curly brackets}"
    step = STEP(message)
    assert step.message, message


def test_nested_steps(called_counters):
    with STEP("Outer step"):
        called_counters.verify_calls(start=1, success=0, end=0, error=0)
        with pytest.raises(CustomError):
            with STEP("Inner step"):
                called_counters.verify_calls(start=2, success=0, end=0, error=0)
                raise CustomError('My exception')
        called_counters.verify_calls(start=2, success=0, end=1, error=1)
    called_counters.verify_calls(start=2, success=1, end=2, error=1)
