import pytest

from shuttlis.geography import Location


@pytest.mark.parametrize("lat,lng", [(90.0, 180.0), (-90.0, -180.0)])
def test_location_constructer_with_valid_values(lat, lng):
    loc = Location(lat, lng)
    assert lat == loc.lat
    assert lng == loc.lng


@pytest.mark.parametrize("lat,lng", [(90.0, 180.0), (-90.0, -180.0)])
def test_location_equality_hash(lat, lng):
    loc = Location(lat, lng)
    loc2 = Location(lat, lng)
    assert loc == loc2
    assert hash(loc) == hash(loc2)


@pytest.mark.skip("Version Mismatch")
def test_location_distance_to():
    l1 = Location(28.434816, 77.049327)
    l2 = Location(28.443195, 77.057225)

    assert 1208.6872544594537 == l1.distance_to(l2).meters


def test_location_distance_to_fast():
    l1 = Location(28.434816, 77.049327)
    l2 = Location(28.443195, 77.057225)

    assert 906.2925481254175 == l1.distance_to_fast(l2).meters


@pytest.mark.parametrize("lat,lng", [(90, 190), (90.1, 179), (90.1, 180.001)])
def test_location_constructer_disallows_lat_lng_values_which_are_out_of_range(lat, lng):
    with pytest.raises(AssertionError):
        Location(lat, lng)
