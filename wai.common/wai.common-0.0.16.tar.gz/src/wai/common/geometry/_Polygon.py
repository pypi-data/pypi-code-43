from typing import List

from ._Point import Point


class Polygon:
    """
    Represents a polygon in 2D integer Cartesian space.
    """
    def __init__(self, *points: Point):
        self.points: List[Point] = list(points)

    def __iter__(self):
        return iter(self.points)
