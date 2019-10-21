import math


class Vector:
    __slots__ = ["x", "y", "z"]

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @staticmethod
    def from_ra_dec(ra, dec):
        cos_dec = math.cos(dec * math.pi / 180.0)
        return Vector(
            math.cos(ra * math.pi / 180.0) * cos_dec,
            math.sin(ra * math.pi / 180.0) * cos_dec,
            math.sin(dec * math.pi / 180.0),
        )

    def magnitude(self):
        return math.sqrt((self.x * self.x + self.y * self.y + self.z * self.z))

    def cross(self, other):
        return self ^ other

    def rcross(self, other):
        x1 = other.x + self.x
        x2 = other.x - self.x
        y1 = other.y + self.y
        y2 = other.y - self.y
        z1 = other.z + self.z
        z2 = other.z - self.z
        return Vector(y1 * z2 - z1 * y2, z1 * x2 - x1 * z2, x1 * y2 - y1 * x2)

    def dot(self, other):
        return self * other

    def normalize(self):
        magnitude = self.magnitude()
        self.x /= magnitude
        self.y /= magnitude
        self.z /= magnitude

    def __mul__(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __xor__(self, other):
        return Vector(
            x=((self.y * other.z) - (self.z * other.y)),
            y=((self.z * other.x) - (self.x * other.z)),
            z=((self.x * other.y) - (self.y * other.x)),
        )

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __repr__(self):
        return "({self.x}, {self.y}, {self.z})".format(self=self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z
