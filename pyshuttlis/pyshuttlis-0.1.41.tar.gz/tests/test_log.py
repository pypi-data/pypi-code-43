import json
import pytest
import logging

from shuttlis.log import configure_logging


def test_log_format_defaults_to_json(capsys):
    logger = configure_logging("pyshuttlis", "DEBUG")
    logger.debug("hey.there")

    captured = capsys.readouterr().err
    assert json.loads(captured)


def test_log_format_can_be_set_to_console(capsys):
    logger = configure_logging("pyshuttlis", "DEBUG", log_format="console")
    logger.debug("hey.there")

    captured = capsys.readouterr().err
    with pytest.raises(json.decoder.JSONDecodeError):
        json.loads(captured)

    assert "hey.there" in captured


def test_extra_is_printed_in_json(capsys):
    logger = configure_logging("pyshuttlis", "DEBUG", log_format="json")
    logger.debug("hey.there", extra={"one": "two"})

    captured = capsys.readouterr().err
    assert "one" in captured
    assert "two" in captured


def test_extra_is_printed_in_console(capsys):
    logger = configure_logging("pyshuttlis", "DEBUG", log_format="console")
    logger.debug("hey.there", extra={"one": "two"})

    captured = capsys.readouterr().err
    assert "one" in captured
    assert "two" in captured


@pytest.mark.xfail
def test_prints_out_exc(capsys):
    """
    TODO: This doesn't seem to work, ValueError isn't logged!
    """
    logger = configure_logging("pyshuttlis", "DEBUG")
    try:
        raise ValueError
    except ValueError:
        logger.error("an.error", exc_info=True)

    captured = capsys.readouterr().err
    assert "an.error" in captured
    assert "ValueError" in captured


@pytest.fixture(autouse=True)
def reset_root_logger():
    yield

    # Pytest's mocks cause issues unless we reset this
    logging.getLogger().handlers = []
