from jivago_streams import Stream
from typing import List, Tuple


def write_dependency_file(dependencies: Tuple[str, List[str]]):
    file = open("dependency.dot", "a+")
    Stream(dependencies[1]).forEach(
        lambda dependency: file.write(f"{dependencies[0]} -> {dependency}\n")
    )
    file.close()


def remove_new_line_character(file: str, imports: str) -> Tuple[str, List[str]]:
    lines_without_new_line_characters = []
    for line in imports:
        lines_without_new_line_characters.append(line.replace("\n", ""))

    return (file, lines_without_new_line_characters)
