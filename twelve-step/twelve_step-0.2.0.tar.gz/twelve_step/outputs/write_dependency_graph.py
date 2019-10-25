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
        origin = normalize_with_dot_standard(dependencies[0])
        destination = normalize_with_dot_standard(dependency)
        output(f"{origin} -> {destination}\n")


def normalize_with_dot_standard(name: str) -> str:
    for reserved_character in ["-", "."]:
        if reserved_character in name:
            return f'"{name}"'
    return name
