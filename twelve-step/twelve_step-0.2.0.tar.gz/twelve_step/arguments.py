from __future__ import annotations
import argparse
from dataclasses import dataclass
from typing import List, Optional


def get_arguments() -> Arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "project_path", help="Path to the project to generate dependency graph for."
    )
    parser.add_argument(
        "-s",
        "--step",
        default=1,
        help="Choose which step of twelve-step you want to execute",
    )
    parser.add_argument(
        "-e",
        "--exclude-packages",
        nargs="*",
        default=[],
        help="List of packages to exclude in graph generation.",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        help="Specifiy the output file name (.dot will be added).",
    )
    arguments = parser.parse_args()
    return Arguments(
        arguments.project_path,
        arguments.step,
        arguments.exclude_packages,
        arguments.output_file,
    )


@dataclass
class Arguments:
    project_path: str
    step: int
    exclude_packages: List[str]
    output_file: Optional[str]
