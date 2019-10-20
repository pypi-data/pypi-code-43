from typing import Callable, List


def construct_exclude_packages(packages_to_exclude: List[str]) -> Callable[[str], bool]:
    def exclude_packages(file_path: str) -> bool:
        return any(
            [excluded_package in file_path for excluded_package in packages_to_exclude]
        )

    return exclude_packages
