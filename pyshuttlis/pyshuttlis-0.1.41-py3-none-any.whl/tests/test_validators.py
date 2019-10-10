from uuid import uuid4

import pytest
from voluptuous import Invalid, MultipleInvalid
from datetime import date

from shuttlis.validators import (
    uuid_validator,
    csv_uuids,
    location,
    military_time,
    coerce_timezone,
)
from shuttlis.time import time_now
from shuttlis.validators import datetime_validator, date_validator


def test_datetime_validator_converts_iso_string_to_datetime():
    time = time_now()
    assert time == datetime_validator(time.isoformat())


@pytest.mark.parametrize(
    "invalid_datetime", ["2013-02-01T12:12:12+5:30", 123123, "random"]
)
def test_datetime_validator_throws_error_when_value_is_not_uuid(invalid_datetime):
    with pytest.raises(ValueError) as e:
        datetime_validator(invalid_datetime)


def test_date_validator_converts_iso_string_to_date():
    assert date(2019, 6, 30) == date_validator("2019-06-30")


@pytest.mark.parametrize("invalid_date", ["02-30-2019", 123123, "random"])
def test_date_validator_throws_error_when_value_is_not_iso_format(invalid_date):
    with pytest.raises(ValueError) as e:
        date_validator(invalid_date)


def test_uuid_validator_converts_string_to_uuid():
    r_uuid = str(uuid4())
    assert r_uuid == uuid_validator(r_uuid)


@pytest.mark.parametrize("invalid_uuid", ["abc", 123])
def test_uuid_validator_throws_error_when_value_is_not_uuid(invalid_uuid):
    with pytest.raises(Invalid) as e:
        uuid_validator(invalid_uuid)


def test_csv_uuid_validator():
    random_uuids = [str(uuid4()) for _ in range(5)]
    csv = ",".join(random_uuids)
    assert random_uuids == csv_uuids(csv)


@pytest.mark.parametrize(
    "lat,lng", [(90.0, 180.0), (-90.0, -180.0), (23.234, 23.234234)]
)
def test_location_validator(lat, lng):
    loc = {"lat": lat, "lng": lng}
    assert loc == location(loc)


@pytest.mark.parametrize("lat,lng", [(90, 190), (90.1, 179), (90.1, 180.001)])
def test_location_validator_disallows_lat_lng_values_which_are_out_of_range(lat, lng):
    with pytest.raises(MultipleInvalid):
        location({"lat": lat, "lng": lng})


@pytest.mark.parametrize("time", [1239, 1903, 209, 905, 945, 0, 2359])
def test_military_time_validator(time):
    assert time == military_time(time)


@pytest.mark.parametrize("time", [20983, -1, 2400, 1760, 161, 2546])
def test_military_validator_disallows_time_values_which_are_out_of_range(time):
    with pytest.raises(Invalid):
        military_time(time)


@pytest.mark.parametrize("tz", ["Asia/Kolkata", "Africa/Casablanca"])
def test_timezone_validator(tz):
    assert tz == coerce_timezone(tz).zone


@pytest.mark.parametrize("tz", ["Asia", "alksjdf"])
def test_timezone_validator_fail(tz):
    with pytest.raises(Invalid):
        coerce_timezone(tz)
