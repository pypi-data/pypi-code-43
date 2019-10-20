from typing import List, Tuple

from twelve_step.outputs.write_dependency_graph import write_dependency_graph


def write_dependency_file(
    dependencies: List[Tuple[str, List[str]]], filename: str
) -> None:
    with open(f"{filename}.dot", "w+") as file:
        write_dependency_graph(dependencies, file.write)
