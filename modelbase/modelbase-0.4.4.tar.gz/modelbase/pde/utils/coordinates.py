import math
import matplotlib.patches as patches
import numpy as np
import itertools
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class _RegularPolygon:
    def __init__(self, *coordinates):
        self.coordinates = coordinates

    def __str__(self):
        return f"{self.coordinates}"

    def __repr__(self):
        return f"{self.coordinates}"

    def __add__(self, other):
        return self.__class__(
            *(i + j for i, j in zip(self.coordinates, other.coordinates))
        )

    def __sub__(self, other):
        return self.__class__(
            *(i - j for i, j in zip(self.coordinates, other.coordinates))
        )

    def __mul__(self, other):
        return self.__class__(
            *(i * j for i, j in zip(self.coordinates, other.coordinates))
        )

    def __pow__(self, other):
        return self.__class__(
            *(i ** j for i, j in zip(self.coordinates, other.coordinates))
        )

    def __truediv__(self, other):
        return self.__class__(
            *(i / j for i, j in zip(self.coordinates, other.coordinates))
        )

    def __floordiv__(self, other):
        return self.__class__(
            *(i // j for i, j in zip(self.coordinates, other.coordinates))
        )

    def __mod__(self, other):
        return self.__class__(
            *(i % j for i, j in zip(self.coordinates, other.coordinates))
        )

    def __iter__(self):
        yield from self.coordinates


# Rod coordinates (1D)


class Rod(_RegularPolygon):
    def __init__(self, x):
        super().__init__(x)
        self.L = 1

    def neighbors(self):
        x = self.coordinates[0]
        return Rod(x - 1), Rod(x + 1)


# TRIANGLE COORDINATES
class Triangle(_RegularPolygon):
    def __init__(self, col, row):
        super().__init__(col, row)
        self.L = 1  # Side length
        self.d = self.L / math.sqrt(3)  # Radius
        self.h = self.L / 2 * math.sqrt(3)  # Height
        self.a = self.h - self.d  # Distance from middle to base
        self.num_vertices = 3
        self.orientation = math.radians(180 * (col % 2 + row % 2))
        self.x_offset = 0.5 * self.L
        self.y_offset = self.a

    def plot(self, ax, facecolor="C1", edgecolor=(0, 0, 0, 1)):
        ax.add_patch(
            patches.RegularPolygon(
                self.to_plot(),
                numVertices=self.num_vertices,
                radius=self.d,
                facecolor=facecolor,
                edgecolor=edgecolor,
                orientation=self.orientation,
            )
        )

    def to_plot(self):
        c, r = self.coordinates
        x = c / 2
        # Only add a if either r or c is odd
        y = r * self.h + (self.a * (r % 2 ^ c % 2))
        return Square(x, y)

    def neighbors(self):
        c, r = self.coordinates
        if c % 2 == r % 2:
            return (Triangle(c + 1, r), Triangle(c, r - 1), Triangle(c - 1, r))
        return (Triangle(c, r + 1), Triangle(c + 1, r), Triangle(c - 1, r))

    def distance(self, Triangle2):
        """Manhattan distance"""
        c1, r1 = self.coordinates
        c2, r2 = Triangle2.coordinates
        return (
            abs(r1 - r2)
            + abs(r1 + (-c1 - r1) / 2 - r2 - (-c2 - r2) / 2)
            + abs((c1 + r1) / 2 - (c2 + r2) / 2)
        )


# SQUARE COORDINATES
class Square(_RegularPolygon):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.L = 1  # side length
        self.r = math.sin(math.pi / 4) * self.L  # Radius
        self.num_vertices = 4
        self.orientation = math.radians(45)
        self.x_offset = 0.5 * self.L
        self.y_offset = 0.5 * self.L

    def plot(self, ax, facecolor="C1", edgecolor=(0, 0, 0, 1)):
        ax.add_patch(
            patches.RegularPolygon(
                self.to_plot(),
                numVertices=self.num_vertices,
                radius=self.r,
                facecolor=facecolor,
                edgecolor=edgecolor,
                orientation=self.orientation,
            )
        )

    def to_oddq(self):
        x, y = self.coordinates
        c = 2 / 3 * x
        r = y / math.sqrt(3) - 0.5 * (c % 2)
        return Oddq(int(c), int(r))

    def to_triangle(self):
        x, y = self.coordinates
        t = Triangle(0, 0)  # Dummy triangle to get height and a
        c = (x - 0.5) * 2
        r = y - t.a
        # Remainder will be 0 or 0.333.., so I can just round it down
        r = round(r / t.h)
        return Triangle(int(c), int(r))

    def to_plot(self):
        x, y = self.coordinates
        return Square(x, y)

    def neighbors(self, directions=(0, 1, 2, 3)):
        x, y = self.coordinates
        surroundings = ((-1, 0), (0, 1), (1, 0), (0, -1))
        result = []
        for direction in directions:
            i, j = surroundings[direction]
            result.append(Square(x + i, y + j))
        return result

    def distance(self, Square2):
        """Manhattan distance"""
        x1, y1 = self.coordinates
        x2, y2 = Square2.coordinates
        return abs(x1 - x2) + abs(y1 - y2)


# HEXAGON COORDINATES
class Oddq(_RegularPolygon):
    def __init__(self, col, row):
        super().__init__(col, row)
        self.L = 1
        self.radius = 1
        self.num_vertices = 6
        self.orientation = math.radians(30)

    def plot(self, ax, facecolor="C1", edgecolor=(0, 0, 0, 1)):
        x, y = self.to_plot()
        ax.add_patch(
            patches.RegularPolygon(
                (x, y),
                numVertices=self.num_vertices,
                radius=self.radius,
                facecolor=facecolor,
                edgecolor=edgecolor,
                orientation=self.orientation,
            )
        )

    def to_plot(self):
        c, r = self.coordinates
        x = 3 / 2 * c
        y = math.sqrt(3) * (r + 0.5 * (c % 2))  # If column is even, shift row
        return Square(float(x), float(y))

    def to_cube(self):
        c, r = self.coordinates
        x = c
        z = r - (c - c % 2) / 2
        y = -x - z
        return Cube(int(x), int(y), int(z))

    def to_axial(self):
        c, r = self.coordinates
        return Axial(int(c), int(r - (c - c % 2) / 2))

    def to_doubleheight(self):
        c, r = self.coordinates
        return Doubleheight(int(c), int(r * 2 + (c % 2)))

    def neighbors(self, directions=(0, 1, 2, 3, 4, 5)):
        """Neighbors of a cell in odd-q coordinates.
        Coordinates start at the upper right and go clockwise
        """
        c, r = self.coordinates
        parity = c % 2
        surroundings = (
            ((1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (0, 1)),
            ((1, 1), (1, 0), (0, -1), (-1, 0), (-1, 1), (0, 1)),
        )

        result = []
        for direction in directions:
            i, j = surroundings[parity][direction]
            result.append(Oddq(c + i, r + j))
        return result

    def distance(self, Oddq2):
        """Manhattan distance"""
        return self.to_cube().distance(Oddq2.to_cube())


class Cube(_RegularPolygon):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def to_oddq(self):
        x, y, z = self.coordinates
        c = x
        r = z + (x - x % 2) / 2
        return Oddq(int(c), int(r))

    def to_axial(self):
        x, y, z = self.coordinates
        return Axial(int(x), int(z))

    def to_doubleheight(self):
        x, y, z = self.coordinates
        c = x
        r = 2 * z + x
        return Doubleheight(c, r)

    def neighbors(self, directions=(0, 1, 2, 3, 4, 5)):
        """Neighbors of a cell in cube coordinates.
        Coordinates start at the upper right and go clockwise
        """
        x, y, z = self.coordinates
        surroundings = (
            (1, -1, 0),
            (1, 0, -1),
            (0, 1, -1),
            (-1, 1, 0),
            (-1, 0, 1),
            (0, -1, 1),
        )
        result = []
        for direction in directions:
            i, j, k = surroundings[direction]
            result.append(Cube(x + i, y + j, z + k))
        return result

    def distance(self, cube2):
        """Distance between two cells c1 and c2 in cube coordinates.
        In a cube grid, Manhattan distances are abs(dx) + abs(dy) + abs(dz).
        The distance on a hex grid is half that:
        d = (abs(x1 - x2) + abs(y1 - y1) + abs(z1 - z2)) / 2
        An equivalent way to write this is by noting that one of the three coordinates
        must be the sum of the other two, then picking that one as the distance:
        d = max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))
        """
        x1, y1, z1 = self.coordinates
        x2, y2, z2 = cube2.coordinates
        return max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2))

    def ring(self, radius):
        """Gives the coordinates of all cells surrounding the center cell with radius r
        Expects cube coordinates.
        """
        x, y, z = self.coordinates
        results = []
        # Go radius * steps in direction +z (4)
        x -= radius
        z += radius

        # Go around each edge
        for direction in range(6):
            # For radius steps
            for j in range(radius):
                c = Cube(x, y, z)
                results.append(c)
                x, y, z = c.neighbors([direction])[0]
        return results


class Axial(_RegularPolygon):
    def __init__(self, q, r):
        super().__init__(q, r)

    def to_oddq(self):
        q, r = self.coordinates
        return Oddq(int(q), int(r + (q - q % 2) / 2))

    def to_cube(coordinates):
        q, r = coordinates
        return Cube(int(q), int(-q - r), int(r))

    def neighbors(self, directions=(0, 1, 2, 3, 4, 5)):
        """Neighbors of a cell in axial coordinates
        Coordinates start at the upper right and go clockwise
        """
        q, r = self.coordinates
        surroundings = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))
        result = []
        for direction in directions:
            i, j = surroundings[direction]
            result.append(Axial(q + i, r + j))
        return result

    def distance(self, Axial2):
        """Manhattan distance"""
        return self.to_cube().distance(Axial2.to_cube())


class Doubleheight(_RegularPolygon):
    def __init__(self, col, row):
        super().__init__(col, row)

    def to_oddq(self):
        c, r = self.coordinates
        return Oddq(int(c), int((r - (c % 2)) / 2))

    def to_cube(self):
        c, r = self.coordinates
        x = c
        z = (r - c) / 2
        y = -x - z
        return Cube(x, y, z)

    def neighbors(self, directions=(0, 1, 2, 3, 4, 5)):
        surroundings = ((+1, +1), (+1, -1), (0, -2), (-1, -1), (-1, +1), (0, +2))
        c, r = self.coordinates
        result = []
        for direction in directions:
            i, j = surroundings[direction]
            result.append(Doubleheight(c + i, r + j))
        return result

    def distance(self, Doubleheight2):
        """Manhattan distance"""
        return self.to_cube().distance(Doubleheight2.to_cube())


class Cube3D(_RegularPolygon):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def to_plot(self):
        x, y, z = self.coordinates
        return Cube3D(x + 0.5, y + 0.5, z + 0.5)

    def plot(self, ax, facecolor, edgecolor):
        cube = [
            [[0, 1, 0], [0, 0, 0], [1, 0, 0], [1, 1, 0]],
            [[0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0]],
            [[1, 0, 1], [1, 0, 0], [1, 1, 0], [1, 1, 1]],
            [[0, 0, 1], [0, 0, 0], [0, 1, 0], [0, 1, 1]],
            [[0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0]],
            [[0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]],
        ]

        cube = np.array(cube) + np.array(self.coordinates)

        ax.add_collection3d(
            Poly3DCollection(
                cube,
                facecolors=list(itertools.repeat(facecolor, 6)),
                edgecolor=edgecolor,
            )
        )

    def neighbors(self, directions=(0, 1, 2, 3, 4, 5)):
        x, y, z = self.coordinates
        surroundings = (
            (-1, 0, 0),
            (0, 1, 0),
            (1, 0, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        )
        result = []
        for direction in directions:
            i, j, k = surroundings[direction]
            result.append(Cube3D(x + i, y + j, z + k))
        return result
