import ctypes
from .clib import _CLIB, is_cgal_cpp_core_supported


class Point:
    """
    Describes a simple two dimensional point.
    """

    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y

    def get_x(self) -> float:
        return self._x

    def get_y(self) -> float:
        return self._y

    def __eq__(self, other):
        return self._x == other.get_x() and self._y == other.get_y()

    def __str__(self):
        return "Point(" + str(self._x) + ", " + str(self._y) + ")"

    def __getitem__(self, index: int):
        if index == 0:
            return self.get_x()
        elif index == 1:
            return self.get_y()
        raise KeyError("Access element " + str(index) + " failed.")


class Instance:
    """
    Describes an instance for the Min Convex Partition Problem.
    This is actually just a set of points.
    To simplify the solutions, each point has a unique sequential index (starting at 0).
    It uses an efficient C++ data structure under the hood which is especially needed
    for the verification process (which is written in C++ for performance).
    """

    # ===================================================================================
    # C-Interface
    # ===================================================================================
    if is_cgal_cpp_core_supported():
        # new_instance()
        _CLIB.new_instance.restype = ctypes.c_void_p
        # delete_instance(void* instance)
        _CLIB.delete_instance.argtypes = [ctypes.c_void_p]
        _CLIB.delete_instance.restype = None
        # add_point_to_instance(void* instance, double x, double y)
        _CLIB.add_point_to_instance.argtypes = [ctypes.c_void_p, ctypes.c_double,
                                                ctypes.c_double]
        _CLIB.add_point_to_instance.restype = ctypes.c_uint64

        class CPoint(ctypes.Structure):
            _fields_ = [("x", ctypes.c_double),
                        ("y", ctypes.c_double)]

        _CLIB.get_point_of_instance.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        _CLIB.get_point_of_instance.restype = CPoint

        _CLIB.num_points_in_instance.argtypes = [ctypes.c_void_p]
        _CLIB.num_points_in_instance.restype = ctypes.c_uint64

    # ===================================================================================

    def __init__(self, name: str = "no_name", points: list = None):
        """
        You can add points either by supplying a list of points or by using the
        add_point() method.
        :param points: List of points (optional)
        """
        self.name = name
        self.meta_data = dict()
        if is_cgal_cpp_core_supported():
            self._cptr = _CLIB.new_instance()
        else:
            self._cptr = None
            self._py_list = []
        if points:
            for point in points:
                self.add_point(point)

    def add_point(self, point: Point) -> int:
        """
        For creating an instance. Adds a point to an instance
        :param point:
        :return: Index of point
        """
        if self._cptr:
                return _CLIB.add_point_to_instance(self._cptr,
                                           float(point[0]),
                                           float(point[1]))
        else:
            i = len(self._py_list)
            self._py_list.append(point)
            return i

    def __eq__(self, other):
        """
        Checks if the two instances have the same points with the same indices.
        The name is neglected.
        :param other: Other Instance
        :return: True iff the points match.
        """
        if len(self) != len(other):
            return False
        for p_a, p_b in zip(self, other):
            if p_a != p_b:
                return False
        return True

    def __iter__(self):
        """
        Iterate over all points in solution
        :return: Iterator
        """
        for i in range(len(self)):
            yield self[i]

    def __len__(self) -> int:
        """
        Number of points in solution
        :return:
        """
        if self._cptr:
            return _CLIB.num_points_in_instance(self._cptr)
        else:
            return len(self._py_list)


    def __getitem__(self, idx) -> Point:
        """
        Returns point on index
        :param idx:
        :return:
        """
        if idx < 0:
            idx = len(self) + idx
        if not (0 <= idx < len(self)):
            raise KeyError("Index " + str(idx) + " out of range.")
        if self._cptr:
            cpoint = _CLIB.get_point_of_instance(self._cptr, idx)
            return Point(cpoint.x, cpoint.y)
        else:
            return self._py_list[idx]

    def __del__(self):
        if self._cptr:
            _CLIB.delete_instance(self._cptr)

    def __str__(self):
        return "Instance(name:"+self.name+", nr_points:"+str(len(self))+")"
