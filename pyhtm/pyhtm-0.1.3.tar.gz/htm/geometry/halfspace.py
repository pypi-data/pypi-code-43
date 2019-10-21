import collections
import math


class Halfspace(collections.namedtuple("Halfspace", ["direction", "distance"])):
    @staticmethod
    def from_direction_and_radius(direction, radius):
        """Create a halfspace from a direction and a raidus (in radians)."""
        distance = math.cos(radius)
        return Halfspace(direction, distance)

    @staticmethod
    def from_direction_and_distance(direction, distance):
        return Halfspace(direction, distance)
