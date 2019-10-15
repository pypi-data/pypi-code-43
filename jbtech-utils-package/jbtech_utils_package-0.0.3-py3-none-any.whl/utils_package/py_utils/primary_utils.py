""" Utilities file for general application use """
import os
import json
import glob
from utils_package.definitions import PACKAGE_DIR, LIB_DIR, CONFIG_PARSER


def get_root_directory():
    """
    Gets the root directory of the path that the project is running from
    :return: String of root directory
    """
    directory = PACKAGE_DIR
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


def open_file(file):
    """
    Gets the contents of a JSON file
    :param file: Fully qualified path and filename
    :return: JSON contents of file
    """
    path = os.path.join(PACKAGE_DIR, LIB_DIR, '%s' % file)
    found_file = glob.glob(path)
    assert len(found_file) == 1, 'Mismatch of number of files! | Search path was %s' % path
    abs_path = os.path.abspath(found_file[0])
    with open(os.path.abspath(found_file[0]), 'r') as raw_file:
        raw_file_contents = raw_file.read()
    if ".json" in abs_path:
        content = json.loads(raw_file_contents)
    else:
        content = raw_file_contents
    return content


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
