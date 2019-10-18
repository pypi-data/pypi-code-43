from typing import List


def find_imports_in_file(file_path: str) -> List[str]:
    with open(file_path) as file:
        return _find_imports(file)


def _find_imports(file) -> List[str]:
    imports = []
    line = file.readline()
    while line:
        if _contains_import(line):
            imports.append(construct_import_line(file, line))
        line = file.readline()
    return imports


def _contains_import(line: str) -> bool:
    return line.startswith("from ")


def construct_import_line(file, line):
    if _multi_line_import(line):
        return _contract_line(file, line)
    return line


def _multi_line_import(line: str) -> bool:
    return "(" in line


def _contract_line(file, line: str) -> str:
    new_line = file.readline()
    while ")" not in new_line:
        line += new_line
        new_line = file.readline()
    line = line.replace("\n", "").replace("(", "")
    return line
