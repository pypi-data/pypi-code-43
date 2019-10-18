from jivago_streams import Stream
from typing import List, Tuple

IMPORT_KEYWORD = " import "


def find_imported_classes_in_imports(file, imports: List[str]) -> Tuple[str, List[str]]:
    classes = (
        Stream(imports)
        .map(_keep_only_classes_portion_of_import_line)
        .map(_extract_classes)
        .flat()
        .filter(_empty_class_name)
        .toList()
    )
    return (file, classes)


def _import_location_in_line(import_line: str) -> int:
    return import_line.index(IMPORT_KEYWORD) + len(IMPORT_KEYWORD)


def _keep_only_classes_portion_of_import_line(import_line: str) -> str:
    return import_line[_import_location_in_line(import_line) :]


def _extract_classes(classes: str) -> List[str]:
    return classes.replace(" ", "").split(",")


def _empty_class_name(class_name: str) -> bool:
    return len(class_name) > 0
