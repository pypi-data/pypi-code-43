import enum
import math

from . import geometry
from .geometry import Vector, Halfspace
from .node import yield_nodes, ROOT_NODES, Node


class Intersection(enum.Enum):
    FULL = 0
    PARTIAL = 1
    NONE = 2


def get_htm_id_level(htm_id):
    return math.floor(math.log(htm_id, 4)) - 1


def _get_htm_root_node(point):
    if point.z < 0.0:
        if point.y > 0.0:
            if point.x > 0.0:
                return ROOT_NODES[0]
            else:
                return ROOT_NODES[1]
        elif point.y == 0.0:
            if point.x >= 0.0:
                return ROOT_NODES[0]
            else:
                return ROOT_NODES[2]
        else:
            if point.x < 0.0:
                return ROOT_NODES[2]
            else:
                return ROOT_NODES[3]
    else:
        if point.y > 0.0:
            if point.x > 0.0:
                return ROOT_NODES[7]
            else:
                return ROOT_NODES[6]
        elif point.y == 0.0:
            if point.x >= 0.0:
                return ROOT_NODES[7]
            else:
                return ROOT_NODES[5]
        else:
            if point.x < 0.0:
                return ROOT_NODES[5]
            else:
                return ROOT_NODES[4]


def get_htm_id(ra, dec, level):
    point = Vector.from_ra_dec(ra, dec)
    node = _get_htm_root_node(point)
    for i in range(level):
        midpoint_1 = node.v2 + node.v0
        midpoint_1.normalize()
        midpoint_2 = node.v0 + node.v1
        midpoint_2.normalize()
        edge = midpoint_2.rcross(midpoint_1)
        if edge * point >= 0.0:
            node = Node(node.v0, midpoint_2, midpoint_1, node.htm_id << 2)
            continue
        midpoint_0 = node.v1 + node.v2
        midpoint_0.normalize()
        edge = midpoint_0.rcross(midpoint_2)
        if edge * point >= 0.0:
            node = Node(node.v1, midpoint_0, midpoint_2, (node.htm_id << 2) + 1)
            continue
        edge = midpoint_1.rcross(midpoint_0)
        if edge * point >= 0.0:
            node = Node(node.v2, midpoint_1, midpoint_0, (node.htm_id << 2) + 2)
            continue
        else:
            node = Node(midpoint_0, midpoint_1, midpoint_2, (node.htm_id << 2) + 3)
    return node.htm_id


def get_htm_circle_region(ra, dec, radius, level, max_ranges=256):
    direction = Vector.from_ra_dec(ra, dec)
    halfspace = Halfspace.from_direction_and_radius(direction, math.radians(radius))
    intersection = intersect_halfspace(halfspace, level=level)
    effective_level = level
    while (len(intersection) > max_ranges) and (effective_level != 0):
        effective_level -= 1
        simplify_ranges(intersection, level - effective_level)
    return intersection


def simplify_ranges(range_list, level):
    """
    Simplify the HTM ranges in `range_list` by an effective level of
    `level`.
    """
    if not range_list or level <= 0:
        raise ValueError
    mask = (0b1 << (2 * level)) - 1
    i = 0
    j = 0
    while i < len(range_list):
        id_min = range_list[i][0] & ~mask
        id_max = range_list[i][1] | mask
        while i < len(range_list) - 1:
            next_ = range_list[i + 1][0] & ~mask
            if next_ > id_max + 1:
                break
            id_max = range_list[i + 1][1] | mask
            i += 1
        range_list[j] = (id_min, id_max)
        i += 1
        j += 1
    range_list[:] = range_list[0:j]


def test_node(node, halfspace):
    count = sum(
        [geometry.point_in_halfspace(v, halfspace) for v in (node.v0, node.v1, node.v2)]
    )
    if count == 3:
        return Intersection.FULL
    elif count == 1 or count == 2:
        return Intersection.PARTIAL
    if not geometry.halfspace_intersects_halfspace(halfspace, node.bounding_circle()):
        return Intersection.NONE
    for edge in ((node.v0, node.v1), (node.v1, node.v2), (node.v2, node.v0)):
        if geometry.edge_intersects_halfspace(*edge, halfspace):
            return Intersection.PARTIAL
    if geometry.halfspace_in_triangle(halfspace, node.v0, node.v1, node.v2):
        return Intersection.PARTIAL
    return Intersection.NONE


def insert_into_range_list(range_list, addition):
    if not range_list:
        range_list += addition
        return
    if range_list[-1][1] + 1 == addition[0][0]:
        range_list[-1] = (range_list[-1][0], addition[0][1])
        range_list += addition[1:]
    else:
        range_list += addition


def intersect_halfspace(halfspace, parent=None, level=20):
    intersection = []
    for node in yield_nodes(parent=parent):
        intersection_type = test_node(node, halfspace)
        if intersection_type == Intersection.FULL:
            lshift = (level * 2 + 4) - (int(math.log2(node.htm_id)) + 1)
            min_ = node.htm_id << lshift
            max_ = min_ + ((2 ** lshift) - 1)
            insert_into_range_list(intersection, [(min_, max_)])
        elif intersection_type == Intersection.PARTIAL:
            if get_htm_id_level(node.htm_id) == level:
                insert_into_range_list(intersection, [(node.htm_id, node.htm_id)])
            else:
                new_ranges = intersect_halfspace(halfspace, parent=node, level=level)
                # Temporary fix for Issue #1
                try:
                    insert_into_range_list(intersection, new_ranges)
                except IndexError:
                    lshift = (level * 2 + 4) - (int(math.log2(node.htm_id)) + 1)
                    min_ = node.htm_id << lshift
                    max_ = min_ + ((2 ** lshift) - 1)
                    insert_into_range_list(intersection, [(min_, max_)])
    return intersection
