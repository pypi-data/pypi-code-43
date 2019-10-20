from typing import Any, Callable, List, Tuple


def write_dependency_graph(
    dependencies: List[Tuple[str, List[str]]], output: Callable[[str], Any]
) -> None:
    output("digraph dependency_graph {\n")

    for dependency in dependencies:
        write_edges(dependency, output)

    output("}\n")


def write_edges(
    dependencies: Tuple[str, List[str]], output: Callable[[str], Any]
) -> None:
    for dependency in dependencies[1]:
        output(f"{dependencies[0]} -> {dependency}\n")
