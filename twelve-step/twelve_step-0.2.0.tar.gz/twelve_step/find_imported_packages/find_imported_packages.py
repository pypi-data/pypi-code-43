from os.path import basename
from typing import List, Tuple

from jivago_streams import Stream

from twelve_step.constants import IMPORT_KEYWORD, FROM_KEYWORD


def find_imported_packages_in_imports(
    file: str, imports: List[str]
) -> Tuple[str, List[str]]:

    packages = (
        Stream(imports)
        .map(_keep_only_packages_portion_of_import_line)
        .map(_extract_package)
        .toList()
    )
    return (file, packages)


def _keep_only_packages_portion_of_import_line(import_line: str) -> str:
    return import_line[
        _from_keyword_location_in_line(import_line) : _import_location_in_line(
            import_line
        )
    ]


def _import_location_in_line(import_line: str) -> int:
    return import_line.index(IMPORT_KEYWORD)


def _from_keyword_location_in_line(import_line: str) -> int:
    return import_line.index(FROM_KEYWORD) + len(FROM_KEYWORD)


def _extract_package(from_package: str) -> str:
    packages = [
        package.replace(" ", "") for package in from_package.split(".") if package != ""
    ]
    return packages[-2] if len(packages) > 1 else packages[-1]
