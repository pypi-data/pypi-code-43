from typing import Dict, Iterator
from zipfile import ZipFile

from .solution import Solution, Edge


class BestSolutionSet:
    """
    This class allows to get a lot of solutions but only keeps the best ones.
    This reduces the overall work as only the best solutions are counted anyways.
    """

    def __init__(self, old_bounds: Dict[str, int] = None):
        """
        :param old_bounds: Edge numbers of already known solutions. Solutions that are not
                            better are discarded to save resources.
        """
        if old_bounds is not None:
            self._old_bounds = old_bounds
        else:
            self._old_bounds = dict()
        self._solutions = dict()

    def add(self, solution: Solution):
        edge_number = len(solution)
        if solution.instance_name in self._old_bounds:
            if self._old_bounds[solution.instance_name] <= edge_number:
                return  # The old bound is better than this solution
        if solution.instance_name in self._solutions:
            if len(self._solutions[solution.instance_name]) <= edge_number:
                return  # There is a better solution already in the set
        self._solutions[solution.instance_name] = solution

    def __getitem__(self, instance_name):
        return self._solutions[instance_name]

    def __iter__(self) -> Iterator[Solution]:
        for solution in self._solutions.values():
            yield solution

