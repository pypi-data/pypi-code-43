import os
import sys

from .instance import Instance
import ctypes

from .solution import Solution
from .clib import is_cgal_cpp_core_supported, cmake_bin, precompiled_bin, \
    try_to_load_clib


class TrivialTriangulationSolver:
    """
    Provides a triangulation as trivial solution. Implemented with
     CGAL Delaunay Triangulation in C++ so it should be pretty fast.
    """
    # ===================================================================================
    # C-Interface
    # ===================================================================================
    if is_cgal_cpp_core_supported():
        __module_name = "cgshop2020_trivial_triangulation_solver_module"
        __paths = {
            "Linux": [
                os.path.join(cmake_bin, "trivial_triangulation_solver",
                             __module_name + ".so"),
                os.path.join(precompiled_bin, "linux-x86_64", "lib" + __module_name + ".so")
            ],
            "Darwin": [
                os.path.join(cmake_bin, "trivial_triangulation_solver",
                             __module_name + ".so"),
                os.path.join(precompiled_bin, "osx", "lib" + __module_name + ".so")
            ], "Windows": [
                os.path.join(cmake_bin, "trivial_triangulation_solver",
                             __module_name + ".dll"),
                os.path.join(precompiled_bin, "win64" if sys.maxsize > 2**32 else "win32", __module_name + ".dll")
            ]
        }
        _CLIB_TTS = try_to_load_clib(__paths)
        _CLIB_TTS.get_solution_by_triangulation.argtypes = [ctypes.c_void_p]
        _CLIB_TTS.get_solution_by_triangulation.restype = ctypes.c_void_p

    # ===================================================================================

    def __call__(self, instance: Instance):
        if not is_cgal_cpp_core_supported():
            raise NotImplementedError(
                "This is only implemented for the version with C++ CGAL Core.")
        solution_cptr = self._CLIB_TTS.get_solution_by_triangulation(instance._cptr)
        solution = Solution(instance=instance, cptr=solution_cptr)
        return solution
