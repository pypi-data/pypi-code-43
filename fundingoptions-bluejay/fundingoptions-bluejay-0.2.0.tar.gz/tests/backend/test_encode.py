import json
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from bluejay.backend.encode import JSONEncoder, datetime_to_rfc3339

# fmt: off
# Black will change the last datetime to have arguments on separate lines.
date_time_to_expected = [
    (datetime(2018, 9, 12, 10, 56, 43, 343), '2018-09-12T10:56:43.000343'),
    (datetime(2018, 12, 30, 23, 23, 0, 0), '2018-12-30T23:23:00'),
    (
        datetime(2018, 12, 30, 23, 23, 0, 0, tzinfo=timezone(timedelta(hours=2))),
        '2018-12-30T23:23:00+02:00'
    ),
    (
        datetime(2018, 12, 30, 23, 23, 0, 0, tzinfo=timezone(-timedelta(hours=3, minutes=43))),
        '2018-12-30T23:23:00-03:43'
    ),
    (
        datetime(2018, 12, 30, 23, 23, 32, 7065, tzinfo=timezone(timedelta(hours=5, minutes=30))),
        '2018-12-30T23:23:32.007065+05:30'
    ),
]
# fmt: on

uuid_to_expected = [
    (
        UUID("634f6fb9-4532-49b0-8f0a-ebf9faf8f588"),
        "634f6fb9-4532-49b0-8f0a-ebf9faf8f588",
    ),
    (
        UUID("4d227dc1-1b5a-46c7-87e8-127fa6fc8046"),
        "4d227dc1-1b5a-46c7-87e8-127fa6fc8046",
    ),
    (
        UUID("7592973f-c365-4e2f-84fe-6403b6af7a4f"),
        "7592973f-c365-4e2f-84fe-6403b6af7a4f",
    ),
    (
        UUID("bede6506-a4eb-4ea7-877a-769a00b23f76"),
        "bede6506-a4eb-4ea7-877a-769a00b23f76",
    ),
]

generic_to_expected = [
    ({"a": "b"}, '{"a": "b"}'),
    ({"c": 1}, '{"c": 1}'),
    ({"d": {"e": "f"}}, '{"d": {"e": "f"}}'),
]


class Sentinel:
    pass


@pytest.mark.parametrize(["dt", "expected"], date_time_to_expected)
def test_datetime_is_converted_to_rfc3339_format(dt, expected):
    formatted = datetime_to_rfc3339(dt)
    assert expected == formatted


@pytest.mark.parametrize(["dt", "expected"], date_time_to_expected)
def test_json_encoder_encodes_datetimes(faker, dt, expected):
    key = faker.pystr()
    input = {key: dt}
    output = JSONEncoder().encode(input)
    expected_output = '{{"{key}": "{expected}"}}'.format(key=key, expected=expected)
    assert expected_output == output


@pytest.mark.parametrize(["uuid", "expected"], uuid_to_expected)
def test_uuid_is_converted_to_string(uuid, expected):
    formatted = str(uuid)
    assert expected == formatted


@pytest.mark.parametrize(["uuid", "expected"], uuid_to_expected)
def test_json_encoder_encodes_uuid(faker, uuid, expected):
    key = faker.pystr()
    input = {key: uuid}
    output = JSONEncoder().encode(input)
    expected_output = '{{"{key}": "{expected}"}}'.format(key=key, expected=expected)
    assert expected_output == output


@pytest.mark.parametrize(["generic", "expected"], generic_to_expected)
def test_generic_is_converted_to_string(generic, expected):
    formatted = json.dumps(generic)
    assert expected == formatted


@pytest.mark.parametrize(["generic", "expected"], uuid_to_expected)
def test_json_encoder_encodes_generic(faker, generic, expected):
    key = faker.pystr()
    input = {key: generic}
    output = JSONEncoder().encode(input)
    expected_output = '{{"{key}": "{expected}"}}'.format(key=key, expected=expected)
    assert expected_output == output


def test_type_error_on_unknown_types():
    with pytest.raises(TypeError):
        JSONEncoder().encode(Sentinel())
