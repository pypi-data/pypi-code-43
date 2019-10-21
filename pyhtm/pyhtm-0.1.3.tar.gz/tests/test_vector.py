import math

import pytest

from htm.geometry import Vector


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (Vector(0, 0, 1), Vector(0, 1, 0), Vector(0, -1, 1)),
        (Vector(0.25, 1, 1), Vector(1, 0.5, 0), Vector(-0.75, 0.5, 1)),
    ],
)
def test_sub(left, right, expected):
    assert left - right == expected


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (Vector(0, 0, 1), Vector(0, 1, 0), Vector(0, 1, 1)),
        (Vector(0.25, 1, 1), Vector(1, 0.5, 0), Vector(1.25, 1.5, 1)),
    ],
)
def test_add(left, right, expected):
    assert left + right == expected


@pytest.mark.parametrize(
    "v0,v1,expected",
    [
        (Vector(0, 0, 1), Vector(0, 1, 0), 0.0),
        (Vector(0.25, 1, 1), Vector(1, 0.5, 0), 0.75),
    ],
)
def test_dot_product(v0, v1, expected):
    assert v0.dot(v1) == v1.dot(v0) == expected


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)),
        (Vector(1, 2, 3), Vector(3, 4, 0), Vector(-12, 9, -2)),
        (Vector(-12, 33, 8), Vector(1.2, 3.4, 11), Vector(335.8, 141.6, -80.4)),
    ],
)
def test_cross_product(left, right, expected):
    assert left.cross(right) == expected


@pytest.mark.parametrize(
    "v,expected",
    [
        (Vector(1, 0, 0), 1),
        (Vector(1, 2, 3), math.sqrt(14)),
        (Vector(1.2, 3.4, 4), 5.38516),
        (Vector(-12, 33, 8), math.sqrt(1297)),
    ],
)
def test_magnitude(v, expected):
    assert v.magnitude() == pytest.approx(expected)


@pytest.mark.parametrize(
    "v,expected",
    [
        (Vector(0, 0, 1), Vector(0, 0, 1)),
        (Vector(0.25, 1, 1), Vector(0.174078, 0.696311, 0.696311)),
    ],
)
def test_normalize(v, expected):
    v.normalize()
    assert v.x == pytest.approx(expected.x, rel=1e-5)
    assert v.y == pytest.approx(expected.y, rel=1e-5)
    assert v.z == pytest.approx(expected.z, rel=1e-5)


@pytest.mark.xfail
def test_normalize_zero_vector():
    Vector(0, 0, 0).normalize()
