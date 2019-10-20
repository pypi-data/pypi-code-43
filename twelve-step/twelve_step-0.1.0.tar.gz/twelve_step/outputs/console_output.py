from typing import List, Tuple

from twelve_step.outputs.write_dependency_graph import write_dependency_graph


def write_dependencies_in_console(dependencies: List[Tuple[str, List[str]]]) -> None:
    write_dependency_graph(dependencies, print)
