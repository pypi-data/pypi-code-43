import collections
import math

from .vector import Vector
from .halfspace import Halfspace

EPSILON = 1e-15


def point_in_halfspace(point, halfspace):
    return halfspace.direction * point > halfspace.distance


def point_in_triangle(point, triangle_v0, triangle_v1, triangle_v2):
    if (
        (triangle_v0 ^ triangle_v1) * point < 0.0
        or (triangle_v1 ^ triangle_v2) * point < 0.0
        or (triangle_v2 ^ triangle_v0) * point < 0.0
    ):
        return False
    return True


def halfspace_intersects_halfspace(halfspace1, halfspace2):
    d = halfspace1.direction * halfspace2.direction
    if d > 1 - EPSILON:
        theta = 0
    elif d < -1 + EPSILON:
        theta = math.pi
    else:
        theta = math.acos(d)
    return theta < (math.acos(halfspace1.distance) + math.acos(halfspace2.distance))


def edge_intersects_halfspace(edge_v0, edge_v1, halfspace):
    gamma1 = edge_v0 * halfspace.direction
    gamma2 = edge_v1 * halfspace.direction
    mu = edge_v0 * edge_v1
    u2 = (1 - mu) / (1 + mu)

    a = -u2 * (gamma1 + halfspace.distance)
    b = gamma1 * (u2 - 1) + gamma2 * (u2 + 1)
    c = gamma1 - halfspace.distance
    D = b * b - 4 * a * c

    if D < 0:
        return False

    q = -0.5 * (b + (math.copysign(1, b) * math.sqrt(D)))
    root1 = float("inf")
    root2 = float("inf")
    if a > EPSILON or a < -EPSILON:
        root1 = q / a
    if q > EPSILON or q < -EPSILON:
        root2 = c / q
    return (root1 >= 0.0 and root1 <= 1.0) or (root2 >= 0.0 and root2 <= 1.0)


def halfspace_in_triangle(halfspace, triangle_v0, triangle_v1, triangle_v2):
    if (triangle_v0 ^ triangle_v1) * halfspace.direction < 0:
        return False
    if (triangle_v1 ^ triangle_v2) * halfspace.direction < 0:
        return False
    if (triangle_v2 ^ triangle_v0) * halfspace.direction < 0:
        return False
    return True
