from typing import Callable, List, Optional, Tuple

from twelve_step.outputs.console_output import write_dependencies_in_console
from twelve_step.outputs.file_output import write_dependency_file


def create_output(
    output_filename: Optional[str]
) -> Callable[[List[Tuple[str, List[str]]]], None]:
    if output_filename is not None:

        def _write_dependency_file(dependencies: List[Tuple[str, List[str]]]) -> None:
            write_dependency_file(dependencies, str(output_filename))

        return _write_dependency_file

    else:
        return write_dependencies_in_console
