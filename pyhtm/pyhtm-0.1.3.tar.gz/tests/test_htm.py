#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `htm` package."""

import math
import os
import pickle

import pytest


import htm
from htm.geometry import Vector, Halfspace
from htm.intersection import Intersection
from htm.node import Node


@pytest.mark.parametrize(
    "v,c,expected",
    [
        (Vector(0, 0, 1), Halfspace(Vector(0, 0, 1), 0.8), True),
        (Vector(0, 0, 1), Halfspace(Vector(0, 0, -1), 0.0), False),
        (
            Vector(1 / math.sqrt(2), 0, 1 / math.sqrt(2)),
            Halfspace(
                Vector(1 / math.sqrt(2), 1 / math.sqrt(2), 0), math.cos(math.pi / 2)
            ),
            True,
        ),
        # Edge Case: Vector on halfspace boundary
        (Vector(0, 0, 1), Halfspace(Vector(0, 1, 0), 0.0), False),
        # Edge Case: Vector just inside halfspace
        (Vector(0, 0, 1), Halfspace(Vector(0, 1, 0), -0.000000001), True),
        # Edge Case: Vector inside halfspace w/ d < 0
        (
            Vector(0, 1 / math.sqrt(2), 1 / math.sqrt(2)),
            Halfspace(Vector(0, 0, -1), -0.8),
            True,
        ),
    ],
)
def test_vertex_in_halfspace(v, c, expected):
    assert htm.geometry.point_in_halfspace(v, c) == expected


@pytest.mark.parametrize(
    "c1,c2,expected",
    [
        (
            Halfspace(Vector(0, 0, 1), 0.0),
            Halfspace(Vector(0, 1, 0), math.cos(math.pi / 8)),
            True,
        ),
        (
            Halfspace(Vector(1 / math.sqrt(3), 1 / math.sqrt(3), 1 / math.sqrt(3)), -1),
            Halfspace(Vector(-1, 0, 0), 0.99),
            True,
        ),
        (
            Halfspace(Vector(1, 0, 0), math.cos(math.pi / 8)),
            Halfspace(Vector(-1, 0, 0), math.cos(math.pi / 8)),
            False,
        ),
        # Edge Case: Halfspaces touch
        (Halfspace(Vector(0, 0, 1), 0.0), Halfspace(Vector(0, 0, -1), 0.0), False),
        # Edge Case: Both halfspaces w/ d < 0
        (Halfspace(Vector(0, 0, 1), -0.1), Halfspace(Vector(0, 0, -1), -0.1), True),
    ],
)
def test_halfspace_intersects_halfspace(c1, c2, expected):
    assert htm.geometry.halfspace_intersects_halfspace(c1, c2) == expected


@pytest.mark.parametrize(
    "edge_v0,edge_v1,halfspace,expected",
    [
        (
            Vector(1, 0, 0),
            Vector(0, 0, 1),
            Halfspace(
                Vector(1 / math.sqrt(2), 0, 1 / math.sqrt(2)), math.cos(math.pi / 8)
            ),
            True,
        ),
        (
            Vector(1, 0, 0),
            Vector(0, 1, 0),
            Halfspace(
                Vector(1 / math.sqrt(3), 1 / math.sqrt(3), 1 / math.sqrt(3)),
                math.cos(0.6154),
            ),
            False,
        ),
        # Edge (heh) Case: Edge inside halfspace
        (
            Vector(1, 0, 0),
            Vector(0, 0, 1),
            Halfspace(Vector(1 / math.sqrt(2), 0, 1 / math.sqrt(2)), 0),
            False,
        ),
        # Edge Case: Edge tangent to halfspace
        (
            Vector(1, 0, 0),
            Vector(0, 0, 1),
            Halfspace(
                Vector(1 / math.sqrt(2), 1 / math.sqrt(2), 0), math.cos(math.pi / 4)
            ),
            False,
        ),
        # Edge Case: Edge starts and ends on halfspace
        (
            Vector(1, 0, 0),
            Vector(0, 1, 0),
            Halfspace(
                Vector(1 / math.sqrt(2), 1 / math.sqrt(2), 0), math.cos(math.pi / 4)
            ),
            True,
        ),
    ],
)
def test_edge_intersects_halfspace(edge_v0, edge_v1, halfspace, expected):
    assert (
        htm.geometry.edge_intersects_halfspace(edge_v0, edge_v1, halfspace) == expected
    )


@pytest.mark.parametrize(
    "c,v0,v1,v2,expected",
    [
        (
            Halfspace(Vector(*([1 / math.sqrt(3)] * 3)), math.cos(math.pi / 8)),
            Vector(0, 1, 0),
            Vector(0, 0, 1),
            Vector(1, 0, 0),
            True,
        ),
        (
            Halfspace(Vector(*([-1 / math.sqrt(3)] * 3)), math.cos(math.pi / 8)),
            Vector(0, 1, 0),
            Vector(0, 0, 1),
            Vector(1, 0, 0),
            False,
        ),
        # Edge Case: Halfspace inscribed in trixel
        (
            Halfspace(Vector(*([1 / math.sqrt(3)] * 3)), math.cos(math.pi / 4)),
            Vector(0, 1, 0),
            Vector(0, 0, 1),
            Vector(1, 0, 0),
            True,
        ),
    ],
)
def test_halfspace_in_trixel(c, v0, v1, v2, expected):
    assert htm.geometry.halfspace_in_triangle(c, v0, v1, v2) == expected


@pytest.mark.parametrize(
    "t,c,expected",
    [
        # Node fully inside halfspace
        (
            Node(
                Vector(0, 1 / math.sqrt(2), 1 / math.sqrt(2)),
                Vector(1 / math.sqrt(2), 0, 1 / math.sqrt(2)),
                Vector(0, 0, 1),
                0b0011,
            ),
            Halfspace(Vector(0, 0, 1), 0.0),
            Intersection.FULL,
        ),
        # Node 2 corners inside halfspace
        (
            Node(
                Vector(0, 1 / math.sqrt(2), 1 / math.sqrt(2)),
                Vector(1 / math.sqrt(2), 0, 1 / math.sqrt(2)),
                Vector(0, 0, -1),
                0b0011,
            ),
            Halfspace(Vector(0, 0, 1), 0.0),
            Intersection.PARTIAL,
        ),
        # Node 1 corner inside halfspace
        (
            Node(
                Vector(0, 1 / math.sqrt(2), 1 / math.sqrt(2)),
                Vector(1 / math.sqrt(2), 0, -1 / math.sqrt(2)),
                Vector(0, 0, -1),
                0b0011,
            ),
            Halfspace(Vector(0, 0, 1), 0.0),
            Intersection.PARTIAL,
        ),
        # Node outside halfspace
        (
            Node(
                Vector(0, 1 / math.sqrt(2), -1 / math.sqrt(2)),
                Vector(1 / math.sqrt(2), 0, -1 / math.sqrt(2)),
                Vector(0, 0, -1),
                0b0011,
            ),
            Halfspace(Vector(0, 0, 1), 0.0),
            Intersection.NONE,
        ),
        # Node edge intersects halfspace
        (
            Node(Vector(0, 1, 0), Vector(0, 0, 1), Vector(1, 0, 0), 0b0011),
            Halfspace(
                Vector(1 / math.sqrt(2), 0, 1 / math.sqrt(2)), math.cos(math.pi / 8)
            ),
            Intersection.PARTIAL,
        ),
        # Halfspace inside trixel
        (
            Node(Vector(0, 1, 0), Vector(0, 0, 1), Vector(1, 0, 0), 0b0011),
            Halfspace(Vector(*([1 / math.sqrt(3)] * 3)), math.cos(math.pi / 8)),
            Intersection.PARTIAL,
        ),
        # Error Case
        (
            Node(Vector(0, 1, 0), Vector(0, 0, -1), Vector(-1, 0, 0), 0b0011),
            Halfspace(Vector(1, 0, 0), 0.01),
            Intersection.NONE,
        ),
    ],
)
def test_trixel(t, c, expected):
    assert htm.intersection.test_node(t, c) == expected


def test_get_htm_id():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data", "htm_ids.p")
    with open(path, "rb") as f:
        htm_ids = pickle.load(f)
    for (ra, dec, expected) in htm_ids:
        actual = htm.get_htm_id(ra, dec, 20)
        assert actual == expected


def test_get_htm_circle_region():
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "htm_ranges.p"
    )
    with open(path, "rb") as f:
        htm_regions = pickle.load(f)
    for i, (ra, dec, radius, level, expected) in enumerate(htm_regions):
        # if level == 20: continue
        # if ra != 224.9472226: continue
        actual = htm.get_htm_circle_region(ra, dec, radius, level)
        assert actual == expected


def test_alerts_database_errors():
    """
    These are RA/DEC coordinates from the ANTARES DB that caused the
    htm library routine `get_htm_id` to error.
    """
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "database_alerts_errors.csv"
    )
    with open(path, "r") as f:
        for line in f:
            _, alert_id, ra, dec, htm_id, _ = line.split(",")
            alert_id = int(alert_id)
            ra = float(ra)
            dec = float(dec)
            htm_id = int(htm_id)
            assert htm.get_htm_id(ra, dec, 20) == htm_id


def test_alerts_database_wrong():
    """
    These are RA/DEC coordinates from the ANTARES DB that caused the
    htm library routine `get_htm_id` to error.
    """
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "database_alerts_wrong.csv"
    )
    with open(path, "r") as f:
        for line in f:
            _, alert_id, ra, dec, htm_id, _ = line.split(",")
            alert_id = int(alert_id)
            ra = float(ra)
            dec = float(dec)
            htm_id = int(htm_id)
            assert htm.get_htm_id(ra, dec, 20) == htm_id


@pytest.mark.xfail
def test_fix_issue_1():
    # This parent node has a child node that registers a PARTIAL
    # intersection with the following halfspace:
    #
    ra = 357.4000082
    dec = 8.9494438
    radius = 0.00028
    #
    # But the intersection routine doesn't find any further intersection
    # with the children of that child node. This should not be possible.
    #
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "issue-1-halfspace.p"
    )
    with open(path, "rb") as f:
        halfspace = pickle.load(f)
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "data", "issue-1-parent.p"
    )
    with open(path, "rb") as f:
        parent = pickle.load(f)
    #
    # The parent has a PARTIAL intersect type
    #
    parent_intersection = htm.intersection.test_node(parent, halfspace)
    assert parent_intersection == htm.intersection.Intersection.PARTIAL
    #
    # But all of the children are NONE
    #
    child_intersections = [
        htm.intersection.test_node(child, halfspace)
        for child in htm.intersection.yield_nodes(parent=parent)
    ]
    assert any(
        [
            intersection != htm.intersection.Intersection.NONE
            for intersection in child_intersections
        ]
    )
