import gzip
from base64 import b64encode

import pytest

from bluejay.backend import SNSBackend
from bluejay.backend.encode import JSONEncoder


@pytest.fixture
def expected_payload(send_event_command):
    obj = send_event_command.payload

    return SNSBackend.compress(JSONEncoder().encode(obj))


def test_compression_duplicate_code(send_event_command, expected_payload):
    payload = send_event_command.payload

    json_payload = JSONEncoder().encode(payload)

    compressed_string = gzip.compress(json_payload.encode())
    b64_payload = b64encode(compressed_string)
    compressed_payload = b64_payload.decode()

    assert compressed_payload == expected_payload
