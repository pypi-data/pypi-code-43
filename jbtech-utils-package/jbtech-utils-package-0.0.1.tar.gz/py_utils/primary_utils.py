""" Utilities file for general application use """
import os
import json
import definitions


def get_root_directory():
    """
    Gets the root directory of the path that the project is running from
    :return: String of root directory
    """
    directory = definitions.ROOT_DIR
    return directory


def get_project_file(file_name, root_d=get_root_directory()):
    """
    Concatenates the filename to the project directory (by default)
    :param file_name: The path relative to the root_d to the file
    :param root_d: The root directory relative to the project
    :return: String of concatenation of root_d and file_name
    """
    config_path = root_d + file_name
    return config_path


def get_json(file):
    """
    Gets the contents of a JSON file
    :param file: Fully qualified path and filename
    :return: JSON contents of file
    """
    w = open(file, 'r')
    with w as content_file:
        contents = json.load(content_file)
    return contents


def create_json(contents, output_file):
    """
    Generates a file in the output_file location with contents
    :param contents: JSON contents for file
    :param output_file: Fully qualified path and filename
    :return: *NONE*
    """
    with open(output_file, 'w') as outfile:
        json.dump(contents, outfile)


def get_current_env():
    """
    Returns the string of the current environment
    :return: String of current environment
    """
    if os.environ.get('DEVENV'):
        environment = os.environ.get('DEVENV')
    else:
        raise KeyError("No configured environment present.")
    return environment
