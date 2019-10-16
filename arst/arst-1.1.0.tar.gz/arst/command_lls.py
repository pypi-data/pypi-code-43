import os.path
import sys
from typing import Optional, Dict

from termcolor_util import green, blue, red, gray

from .file_resolver import FileResolver, FileEntry
from .project_reader import read_project_definition, ProjectDefinition, parse_file_name, ParsedFile


def process_folder(current_path: str,
                   file_resolver: FileResolver,
                   project_parameters: Dict[str, str],
                   path_mappings: Dict[str, FileEntry]) -> None:
    """
    Recursively process the handlebars templates for the given project.
    """
    for file_entry in file_resolver.listdir():
        file: ParsedFile = parse_file_name(file_entry.name, project_parameters)
        full_local_path = os.path.join(current_path, file.name)

        if file_entry.name == "HELP.md" or file_entry.name == ".ars":
            continue

        path_mappings[os.path.normpath(full_local_path)] = file_entry


def list_folder_in_project(projects_folder: str,
                           folder_to_list: str,
                           loaded_project_parameters: Optional[Dict[str, str]]) -> None:
    if not loaded_project_parameters:
        print(red("Unable to find a project. .ars file is missing."))
        sys.exit(1)

    project_name = loaded_project_parameters["NAME"]

    project_definition: ProjectDefinition = read_project_definition(projects_folder, project_name)
    path_mappings: Dict[str, FileEntry] = dict()
    process_folder(folder_to_list,
                   project_definition.file_resolver().subentry(path=folder_to_list),
                   loaded_project_parameters,
                   path_mappings)

    local_files = os.listdir(folder_to_list)

    def is_dir(name: str) -> bool:
        return os.path.isdir(os.path.join(folder_to_list, name))

    local_files.sort(key=lambda it: (not is_dir(it), it.lower()))

    for file in local_files:
        local_path_name = os.path.normpath(os.path.join(folder_to_list, file))
        if local_path_name in path_mappings:
            file_entry = path_mappings[local_path_name]

            if file_entry.is_dir:
                print(blue(file, bold=True),
                      gray(f"({file_entry.owning_project})", bold=True))
            elif file_entry.is_exe:
                print(green(file, bold=True),
                      gray(f"({file_entry.owning_project})", bold=True))
            else:
                print(file,
                      gray(f"({file_entry.owning_project})", bold=True))
        else:
            if os.path.isdir(local_path_name):
                print(blue(file, bold=True),
                      red(f"(local)", bold=False))
            elif os.access(local_path_name, os.X_OK):
                print(green(file, bold=True),
                      red(f"(local)", bold=False))
            else:
                print(file,
                      red(f"(local)", bold=False))
