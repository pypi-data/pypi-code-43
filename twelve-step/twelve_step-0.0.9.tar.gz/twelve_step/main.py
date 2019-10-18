import argparse
from os import walk

from jivago_streams import Stream

from typing import List, Tuple

from twelve_step.dependency_graph import (
    remove_new_line_character,
    write_dependency_file,
)
from twelve_step.find_classes.find_classes import find_classes
from twelve_step.find_imports.find_imports_in_file import find_imports_in_file
from twelve_step.find_imported_classes.find_imported_classes_in_imports import (
    find_imported_classes_in_imports,
)


def python_file(file):
    return file.endswith("py")


def _find_imports_in_file(file_path: str) -> Tuple[str, List[str]]:
    return (file_path, find_imports_in_file(file_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path")
    args = parser.parse_args()

    file = open("dependency.dot", "a+")
    file.write("digraph dependency_graph {\n")
    file.close()

    for (path, directories, files) in walk(args.project_path):
        construct_file_path = lambda file: f"{path}/{file}"
        (
            Stream(files)
            .filter(python_file)
            .map(construct_file_path)
            .map(_find_imports_in_file)
            .map(find_imported_classes_in_imports)
            .map(remove_new_line_character)
            .map(find_classes)
            .flat()
            .forEach(write_dependency_file)
        )

    file = open("dependency.dot", "a+")
    file.write("}\n")
    file.close()


if __name__ == "__main__":
    main()
