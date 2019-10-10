from dataclasses import dataclass
from typing import List
from shapely.geometry import Point, LineString

from geopy.distance import geodesic, Distance
from geo.ellipsoid import distance


@dataclass
class Location:
    lat: float
    lng: float

    def __init__(self, lat: float, lng: float):
        assert -90 <= lat <= 90
        assert -180 <= lng <= 180
        self.lat = lat
        self.lng = lng

    def __eq__(self, o: object) -> bool:
        return (self.lat, self.lng) == (o.lat, o.lng)

    def __hash__(self) -> int:
        return hash((self.lat, self.lng))

    def as_point(self):
        return Point(self.lng, self.lat)

    def distance_to(self, other) -> Distance:
        loc1 = (self.lat, self.lng)
        loc2 = (other.lat, other.lng)
        return geodesic(loc1, loc2)

    def distance_to_fast(self, other) -> Distance:
        loc1 = (self.lat, self.lng)
        loc2 = (other.lat, other.lng)
        return Distance(kilometers=distance(loc1, loc2) / 1000)


@dataclass
class Path:
    def __init__(self, locations: List[Location]):
        assert len(locations) >= 2
        points = [location.as_point() for location in locations]
        self._path = LineString([[p.x, p.y] for p in points])

    def as_list(self):
        return [Location(lat=y, lng=x) for x, y in self._path.coords]
