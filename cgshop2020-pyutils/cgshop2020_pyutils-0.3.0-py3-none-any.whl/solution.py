import ctypes
from .clib import _CLIB, is_cgal_cpp_core_supported
from typing import Union
from .instance import Instance


class Edge:
    """
    An edge contains the vertex indices to its source and target.
    They are automatically sorted such that i<=j.
    """

    def __init__(self, i: int, j: int):
        self._i = min(i, j)
        self._j = max(i, j)

    def __str__(self):
        return "Edge(" + str(self._i) + ',' + str(self._j) + ")"

    def __eq__(self, other):
        return other.get_i() == self.get_i() and other.get_j() == self.get_j()

    def get_i(self) -> int:
        return self._i

    def get_j(self) -> int:
        return self._j

    def __hash__(self):
        return hash((self._i, self._j))

    def __getitem__(self, index: int):
        if index == 0:
            return self.get_i()
        elif index == 1:
            return self.get_j()
        raise KeyError("Access element " + str(index) + " failed.")


class Solution:
    """
    Encodes a solution, which is a list of edges on point indices.
    The instance is not referenced, you have to remember which instance this solution
    was for.

    Warning: While this class supports hash, it is rather inefficient especially if you
            want to have multiple solutions for the same instance. It actually justs
            hashes the instance name. The equality operator checks if all edges are
            identical, which can take some time.
    """

    # ===================================================================================
    # C-Interface
    # ===================================================================================
    if is_cgal_cpp_core_supported():
        # Create solution
        _CLIB.new_solution.argtypes = []
        _CLIB.new_solution.restype = ctypes.c_void_p  # void* on C++ Solution object
        # delete_solution(void* solution)
        _CLIB.delete_solution.argtypes = [ctypes.c_void_p]
        _CLIB.delete_solution.restype = None
        # add_edge_to_solution(void* solution, int i, int j)
        _CLIB.add_edge_to_solution.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                               ctypes.c_int]
        _CLIB.add_edge_to_solution.restype = None

        # void make_solution_unique(void* solution)
        _CLIB.make_solution_unique.argtypes = [ctypes.c_void_p]
        _CLIB.make_solution_unique.restype = None

        class CEdge(ctypes.Structure):
            _fields_ = [("i", ctypes.c_uint64),
                        ("j", ctypes.c_uint64)]

        # get_edge_of_solution(void* solution, uint64_t index) -> CEdge
        _CLIB.get_edge_of_solution.argtypes = [ctypes.c_void_p, ctypes.c_uint64]
        _CLIB.get_edge_of_solution.restype = CEdge
        # num_edges_in_solution(void* solution) -> uint64_t
        _CLIB.num_edges_in_solution.argtypes = [ctypes.c_void_p]
        _CLIB.num_edges_in_solution.restype = ctypes.c_uint64

    # ===================================================================================

    def __init__(self, instance: Union[str, Instance], edges: list = None, cptr=None):
        """
        Create a solution object. Add the edges afterwards with add_edge(Edge(i, j))
        :param instance: Instance or name of instance
        :param cptr: If you want to create a python Solution based on a
                        pointer to a C++ Solution
        """
        if type(instance) is str:
            self.instance_name = instance
        else:
            self.instance_name = instance.name
        self.meta_data = dict()
        if cptr:
            self._cptr = cptr
        else:
            if is_cgal_cpp_core_supported():
                self._cptr = _CLIB.new_solution()
            else:
                self._cptr = None
                self._py_list = []
        if edges:
            for edge in edges:
                self.add_edge(edge)

    def __iter__(self):
        """
        Iterate over all edges
        :return: Iterator
        """
        for i in range(len(self)):
            yield self[i]

    def __hash__(self):
        """
        Warning: Super inefficient.
        :return:
        """
        return self.instance_name.__hash__()

    def __getitem__(self, index):
        """
        Return the i-th edge in the solution.
        :param index: index < len
        :return: Edge
        """
        if index < 0:
            index = len(self) + index
        if not (0 <= index < len(self)):
            raise KeyError("Index " + str(index) + " out of range.")
        if self._cptr:
            cedge = _CLIB.get_edge_of_solution(self._cptr, index)
            return Edge(cedge.i, cedge.j)
        else:
            return self._py_list[index]

    def add_edge(self, edge: Edge) -> None:
        """
        Add an edge to the solution
        :param edge: Edge to be added
        :return: None
        """
        if self._cptr:
            _CLIB.add_edge_to_solution(self._cptr, int(edge[0]), int(edge[1]))
        else:
            self._py_list.append(edge)

    def delete_double_edges(self):
        """
        Remove redundant occurrences of edges in solution (double edges).
        :return:
        """
        if self._cptr:
            _CLIB.make_solution_unique(self._cptr)
        else:
            self._py_list = list(set(self._py_list))
        return self

    def __len__(self) -> int:
        """
        Number of edges in the solution
        :return: int
        """
        if self._cptr:
            return _CLIB.num_edges_in_solution(self._cptr)
        else:
            return len(self._py_list)

    def __eq__(self, other) -> bool:
        """
        Checks if both solutions contain the same edges
        :param other:
        :return:
        """
        if self.instance_name != other.instance_name:
            return False
        return set(e for e in self) == set(e for e in other)

    def __del__(self):
        if self._cptr:
            _CLIB.delete_solution(self._cptr)

    def __str__(self):
        return "Solution(instance:" + self.instance_name + ", nr_edges:" + str(
            len(self)) + ")"
