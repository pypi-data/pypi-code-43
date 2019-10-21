import collections

from .geometry import Vector, Halfspace


class Node(collections.namedtuple("Node", ["v0", "v1", "v2", "htm_id"])):
    def bounding_circle(self):
        direction = (self.v1 - self.v0) ^ (self.v2 - self.v1)
        direction.normalize()
        distance = self.v0 * direction
        return Halfspace(direction, distance)

    def yield_children(self):
        w0 = self.v1 + self.v2
        w0.normalize()
        w1 = self.v0 + self.v2
        w1.normalize()
        w2 = self.v0 + self.v1
        w2.normalize()
        yield Node(self.v0, w2, w1, (self.htm_id << 2) + 0)
        yield Node(self.v1, w0, w2, (self.htm_id << 2) + 1)
        yield Node(self.v2, w1, w0, (self.htm_id << 2) + 2)
        yield Node(w0, w1, w2, (self.htm_id << 2) + 3)


ROOT_VERTICES = [
    Vector(0, 0, 1),
    Vector(1, 0, 0),
    Vector(0, 1, 0),
    Vector(-1, 0, 0),
    Vector(0, -1, 0),
    Vector(0, 0, -1),
]


ROOT_NODES = [
    Node(ROOT_VERTICES[1], ROOT_VERTICES[5], ROOT_VERTICES[2], 0b1000),
    Node(ROOT_VERTICES[2], ROOT_VERTICES[5], ROOT_VERTICES[3], 0b1001),
    Node(ROOT_VERTICES[3], ROOT_VERTICES[5], ROOT_VERTICES[4], 0b1010),
    Node(ROOT_VERTICES[4], ROOT_VERTICES[5], ROOT_VERTICES[1], 0b1011),
    Node(ROOT_VERTICES[1], ROOT_VERTICES[0], ROOT_VERTICES[4], 0b1100),
    Node(ROOT_VERTICES[4], ROOT_VERTICES[0], ROOT_VERTICES[3], 0b1101),
    Node(ROOT_VERTICES[3], ROOT_VERTICES[0], ROOT_VERTICES[2], 0b1110),
    Node(ROOT_VERTICES[2], ROOT_VERTICES[0], ROOT_VERTICES[1], 0b1111),
]


def yield_nodes(parent=None):
    if parent is None:
        yield from ROOT_NODES
    else:
        yield from parent.yield_children()
