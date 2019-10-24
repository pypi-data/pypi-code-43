from .instance import Instance
from .solution import Solution
from .clib import _CLIB, is_cgal_cpp_core_supported
import ctypes


class SolutionStatus(ctypes.Structure):
    """
    Contains the feasibility of a checked solution. If it is infeasible, a message is
    attached, describing the error. Otherwise, the objective value is attached.
    """

    # ===================================================================================
    # C-Interface
    # ===================================================================================
    _fields_ = [("_cstr_msg", ctypes.c_char_p),
                ("_obj_val", ctypes.c_int64), ]
    if is_cgal_cpp_core_supported():
        _CLIB.VerificationResult_destructor.argtypes = [ctypes.c_void_p]
        _CLIB.VerificationResult_destructor.restype = None

    # ===================================================================================

    def is_feasible(self) -> bool:
        """
        Returns true if the solution is feasible.
        :return: bool
        """
        return self._obj_val >= 0

    def get_message(self) -> str:
        """
        A message describing what is wrong with the instance.
        :return: str
        """
        return self._cstr_msg.decode("utf-8")

    def get_objective_value(self) -> int:
        """
        If the solution is feasible, there is an objective value.
        :return: int
        """
        return int(self._obj_val)

    def __str__(self):
        return "SolutionStatus(is_feasible:"+str(self.is_feasible())+", msg:"+self.get_message()+", obj:"+str(self.get_objective_value())+")"

    def __del__(self):
        _CLIB.VerificationResult_destructor(ctypes.byref(self))

    def __bool__(self):
        return self.is_feasible()


class SolutionChecker:
    """
    Checks if a solution is feasible and also computes the objective value.
    We use CGAL (C++) with exact arithmetic in the background to make sure that
    there are no floating point errors. The performance is reasonably efficient for
    verifying even large instances but might be too slow for high-frequency use
    in meta-heuristics.
    """
    # ===================================================================================
    # C-Interface
    # ===================================================================================
    if is_cgal_cpp_core_supported():
        _CLIB.check_solution.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        _CLIB.check_solution.restype = SolutionStatus

    # ===================================================================================

    def __call__(self, instance: Instance, solution: Solution) -> SolutionStatus:
        """
        Given an instance and a corresponding solution, this function checks if
        the solutions is feasible for this instance.
        :param instance: Instance
        :param solution: Solution for the instance
        :return: SolutionStatus with all the information.
        """
        if not is_cgal_cpp_core_supported():
            raise NotImplementedError("Only supported with C++ CGAL Core.")
        return _CLIB.check_solution(solution._cptr, instance._cptr)
