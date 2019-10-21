import math

import pytest

from htm.node import Node
from htm.geometry import Vector, Halfspace


@pytest.mark.parametrize(
    "t,expected",
    [
        (
            Node(Vector(0, 1, 0), Vector(0, 0, 1), Vector(1, 0, 0), 0b0011),
            Halfspace(
                Vector(1 / math.sqrt(3), 1 / math.sqrt(3), 1 / math.sqrt(3)),
                1 / math.sqrt(3),
            ),
        )
    ],
)
def test_bounding_circle(t, expected):
    bounding_circle = t.bounding_circle()
    assert bounding_circle.direction == expected.direction
    assert bounding_circle.distance == expected.distance


def test_yield_children():
    v0 = Vector(0, 1, 0)
    v1 = Vector(0, 0, 1)
    v2 = Vector(1, 0, 0)
    w0 = v1 + v2
    w0.normalize()
    w1 = v0 + v2
    w1.normalize()
    w2 = v0 + v1
    w2.normalize()
    t = Node(Vector(0, 1, 0), Vector(0, 0, 1), Vector(1, 0, 0), 0b1111)
    children = list(t.yield_children())
    assert len(children) == 4
    assert children[0] == Node(v0, w2, w1, 0b111100)
    assert children[1] == Node(v1, w0, w2, 0b111101)
    assert children[2] == Node(v2, w1, w0, 0b111110)
    assert children[3] == Node(w0, w1, w2, 0b111111)
