import logging

import pytest

from bluejay.backend.encode import JSONEncoder
from bluejay.backend.logging import LoggingBackend

_default_logging_level = logging.INFO
_default_logging_location = "bluejay.backend.logging"


@pytest.fixture
def expected_json(send_event_command):
    obj = {
        "event": send_event_command.event_name,
        "payload": send_event_command.payload,
    }

    # We know the encoder works, due to :tests.backend.test_encode:, so use it here for convenience.
    return JSONEncoder().encode(obj)


@pytest.fixture
def backend():
    return LoggingBackend()


def test_backend_takes_a_SendEvent_command(send_event_command, backend):
    result = backend.send(send_event_command)
    assert result.success is True


def test_backend_logs_as_expected(caplog, send_event_command, backend):
    expected_level = _default_logging_level
    expected_location = _default_logging_location

    with caplog.at_level(expected_level, logger=expected_location):
        backend.send(send_event_command)

    assert len(caplog.records) >= 1


def test_backend_logs_expected_json(caplog, send_event_command, backend, expected_json):
    with caplog.at_level(_default_logging_level, logger=_default_logging_location):
        backend.send(send_event_command)

    logged_messages = [r.message for r in caplog.records]
    assert expected_json in logged_messages
