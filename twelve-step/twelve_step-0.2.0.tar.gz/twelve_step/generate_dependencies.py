from os import walk
from os.path import dirname, basename
from twelve_step.find_imported_packages.find_imported_packages import (
    find_imported_packages_in_imports,
)
from typing import List, Callable, Tuple

from jivago_streams import Stream

from twelve_step.find_classes.find_classes import find_classes
from twelve_step.find_imported_classes.find_imported_classes_in_imports import (
    find_imported_classes_in_imports,
)
from twelve_step.find_imports.find_imports_in_file import find_imports_in_file


def generate_class_dependencies(
    project_path: str, excluded_packages: Callable[[str], bool]
) -> List[Tuple[str, List[str]]]:

    return generate_dependencies(
        project_path, excluded_packages, _generate_class_dependencies
    )


def _generate_class_dependencies(
    path: str, files: List[str], in_excluded_packages: Callable[[str], bool]
) -> List[Tuple[str, List[str]]]:

    return (
        _find_all_imports(files, path, in_excluded_packages)
        .map(find_imported_classes_in_imports)
        .map(remove_new_line_character)
        .map(find_classes)
        .flat()
        .toList()
    )


def generate_packages_dependencies(
    project_path: str, excluded_packages: Callable[[str], bool]
) -> List[Tuple[str, List[str]]]:

    return generate_dependencies(
        project_path, excluded_packages, _generate_packages_dependencies
    )


def generate_dependencies(
    project_path: str,
    excluded_packages: Callable[[str], bool],
    _generate_dependencies: Callable[
        [str, List[str], Callable], List[Tuple[str, List[str]]]
    ],
) -> List[Tuple[str, List[str]]]:
    nested_dependencies = [
        _generate_dependencies(path, files, excluded_packages)
        for path, directories, files in walk(project_path)
    ]
    return [
        dependency
        for dependencies in nested_dependencies
        for dependency in dependencies
    ]


def _generate_packages_dependencies(
    path: str, files: List[str], in_excluded_packages: Callable[[str], bool]
) -> List[Tuple[str, List[str]]]:
    def extract_package(
        file: str, imported_packages: List[str]
    ) -> Tuple[str, List[str]]:
        return (basename(dirname(file)), imported_packages)

    return (
        _find_all_imports(files, path, in_excluded_packages)
        .map(find_imported_packages_in_imports)
        .map(remove_new_line_character)
        .map(extract_package)
        .toList()
    )


def _find_all_imports(
    files: List[str], path: str, in_excluded_packages: Callable[[str], bool]
) -> Stream:
    remove_excluded_packages_from_imports = construct_remove_excluded_packages_from_imports(
        in_excluded_packages
    )

    def construct_filepath(file: str) -> str:
        return f"{path}/{file}"

    def excluded_packages(filepath: str) -> bool:
        return not in_excluded_packages(filepath)

    return (
        Stream(files)
        .filter(python_file)
        .map(construct_filepath)
        .filter(excluded_packages)
        .map(find_imports_in_file)
        .map(remove_excluded_packages_from_imports)
    )


def python_file(file):
    return file.endswith(".py")


def construct_remove_excluded_packages_from_imports(
    in_excluded_packages: Callable[[str], bool]
) -> Callable[[str, List[str]], Tuple[str, List[str]]]:
    def filtering_function(file_path: str, imports: List[str]):
        return (
            file_path,
            [package for package in imports if not in_excluded_packages(package)],
        )

    return filtering_function


def remove_new_line_character(file: str, imports: str) -> Tuple[str, List[str]]:
    lines_without_new_line_characters = []
    for line in imports:
        lines_without_new_line_characters.append(line.replace("\n", ""))

    return (file, lines_without_new_line_characters)
