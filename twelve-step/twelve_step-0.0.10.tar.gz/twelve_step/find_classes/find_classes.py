from typing import List, Tuple

CLASS_KEYWORD = "class "


def find_classes(file: str, imported_classes: List[str]) -> List[Tuple[str, List[str]]]:
    with open(file) as file:
        lines = file.readlines()
        classes = _find_classes_in(lines)
    return [(clazz, imported_classes) for clazz in classes]


def _find_classes_in(lines: List[str]):
    return [
        _find_class_name_in(line) for line in lines if line.startswith(CLASS_KEYWORD)
    ]


def _find_class_name_in(line: str) -> str:
    end_of_class_name_index = line.find("(") if line.find("(") != -1 else line.find(":")
    start_of_class_name_index = len(CLASS_KEYWORD)
    return line[start_of_class_name_index:end_of_class_name_index]
