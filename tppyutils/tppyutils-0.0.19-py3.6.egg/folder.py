#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility methods related to folders
"""


from __future__ import print_function, division, absolute_import


import os
import sys
import shutil
import tempfile
import traceback
import subprocess
import fnmatch

import tpPyUtils


def create_folder(name, directory=None, make_unique=False):
    """
    Creates a new folder on the given path and with the given name
    :param name: str, name of the new directory
    :param directory: str, path to the new directory
    :param make_unique: bool, Whether to pad the name with a number to make it unique if the folder is not unique
    :return: variant, str || bool, folder name with path or False if the folder creation failed
    """

    from tpPyUtils import path

    full_path = False

    if directory is None:
        full_path = name

    if not name:
        full_path = directory

    if name and directory:
        full_path = path.join_path(directory, name)

    if make_unique:
        full_path = path.join_path(directory, name)

    if not full_path:
        return False

    if path.is_dir(full_path):
        return full_path

    try:
        os.makedirs(full_path)
    except Exception as e:
        return False

    return full_path


def rename_folder(directory, name, make_unique=False):
    """
    Renames given with a new name
    :param directory: str, full path to the diretory we want to rename
    :param name: str, new name of the folder we want to rename
    :param make_unique: bool, Whether to add a number to the folder name to make it unique
    :return: str, path of the renamed folder
    """

    from tpPyUtils import path

    base_name = path.get_basename(directory=directory)
    if base_name == name:
        return

    parent_path = path.get_dirname(directory=directory)
    rename_path = path.join_path(parent_path, name)

    if make_unique:
        rename_path = path.unique_path_name(directory=rename_path)

    if path.is_dir(rename_path) or path.is_file(rename_path):
        return False

    try:
        os.chmod(directory, 0o777)
        message = 'rename: {0} >> {1}'.format(directory, rename_path)
        tpPyUtils.logger.info(message)
        os.rename(directory, rename_path)
    except Exception:
        tpPyUtils.logger.error('{}'.format(traceback.format_exc()))
        return False

    return rename_path


def copy_folder(directory, directory_destination, ignore_patterns=[]):
    """
    Copy the given directory into a new directory
    :param directory: str, directory to copy with full path
    :param directory_destination: str, destination directory
    :param ignore_patterns: list<str>, extensions we want to ignore when copying folder elements
    If ['txt', 'py'] is given all py and text extension files will be ignored during the copy operation
    :return: str, destination directory
    """

    from tpPyUtils import path

    if not path.is_dir(directory=directory):
        return
    if not ignore_patterns:
        shutil.copytree(directory, directory_destination)
    else:
        shutil.copytree(directory, directory_destination, ignore=shutil.ignore_patterns(ignore_patterns))

    return directory_destination


def move_folder(path1, path2):
    """
    Moves the folder pointed by path1 under the directory path2
    :param path1: str, folder with full path
    :param path2: str, path where path1 should be move into
    :return: bool, Whether the move operation was successfully
    """

    try:
        shutil.move(path1, path2)
    except:
        tpPyUtils.logger.warning('Failed to move {0} to {1}'.format(path1, path2))
        return False

    return True


def delete_folder(folder_name, directory):
    """
    Deletes the folder by name in the given directory
    :param folder_name: str, name of the folder to delete
    :param directory: str, the directory path where the folder is stored
    :return: str, folder that was deleted with path
    """

    from tpPyUtils import path, fileio

    def delete_read_only_error(action, name, exc):
        """
        Helper to delete read only files
        """

        os.chmod(name, 0o777)
        action(name)

    full_path = path.join_path(directory, folder_name)
    if not path.is_dir(full_path):
        return None

    shutil.rmtree(full_path, onerror=delete_read_only_error)

    return full_path


def clean_folder(directory):
    """
    Removes everything in the given directory
    :param directory: str
    """

    from tpPyUtils import path, fileio, folder

    base_name = path.get_basename(directory=directory)
    dir_name = path.get_dirname(directory=directory)

    if path.is_dir(directory):
        files = folder.get_files(directory)
        for f in files:
            fileio.delete_file(f, directory)

        delete_folder(base_name, dir_name)

    if not path.is_dir(directory):
        create_folder(base_name, dir_name)


def get_folder_size(directory, round_value=2):
    """
    Returns the size of the given folder
    :param directory: str
    :param round_value: int, value to round size to
    :return: str
    """

    from tpPyUtils import path, fileio

    size = 0
    for root, dirs, files in os.walk(directory):
        for name in files:
            size += fileio.get_file_size(path.join_path(root, name), round_value)

    return size


def get_size(file_path, round_value=2):
    """
    Return the size of the given directory or file path
    :param file_path: str
    :param round_value: int, value to round size to
    :return: int
    """

    from tpPyUtils import fileio, path

    size = 0
    if path.is_dir(file_path):
        size = get_folder_size(file_path, round_value)
    if path.is_file(file_path):
        size = fileio.get_file_size(file_path, round_value)

    return size


def get_sub_folders(root_folder, sort=True):
    """
    Return a list with all the sub folders names on a directory
    :param root_folder: str, folder we want to search sub folders for
    :param sort: bool, True if we want sort alphabetically the returned folders or False otherwise
    :return: list<str>, sub folders names
    """

    if not os.path.exists(root_folder):
        raise RuntimeError('Folder {0} does not exists!'.format(root_folder))
    file_names = os.listdir(root_folder)
    result = list()
    for f in file_names:
        if os.path.isdir(os.path.join(os.path.abspath(root_folder), f)):
            result.append(f)
    if sort:
        result.sort()

    return result


def get_folders(root_folder, recursive=False):
    """
    Get folders found in the root folder
    :param root_folder: str, folder we ant to search folders on
    :param recursive: bool, Whether to search in all root folder child folders or not
    :return: list<str>
    """

    from tpPyUtils import path

    found_folders = list()
    if not recursive:
        try:
            found_files = os.listdir(root_folder)
        except:
            return found_folders

        if not found_files:
            return found_folders
        for file_name in found_files:
            folder_name = path.join_path(root_folder, file_name)
            if path.is_dir(folder_name):
                folder_name = os.path.relpath(folder_name, root_folder)
                folder_name = path.clean_path(folder_name)
                found_folders.append(folder_name)
    else:
        try:
            for root, dirs, files in os.walk(root_folder):
                for d in dirs:
                    folder_name = path.join_path(root, d)
                    folder_name = os.path.relpath(folder_name, root_folder)
                    folder_name = path.clean_path(folder_name)
                    found_folders.append(folder_name)
        except:
            return found_folders

    return found_folders


def get_files(root_folder, full_path=False, recursive=False, pattern="*"):
    """
    Returns files found in the given folder
    :param root_folder: str, folder we want to search files on
    :param full_path: bool, if true, full path to the files will be returned otherwise file names will be returned
    :return: list<str>
    """

    from tpPyUtils import path

    if not path.is_dir(root_folder):
        return []

    # TODO: For now pattern only works in recursive searches. Fix it to work on both

    found = list()

    if recursive:
        for dir_path, dir_names, file_names in os.walk(root_folder):
            for file_name in fnmatch.filter(file_names, pattern):
                if full_path:
                    found.append(os.path.join(dir_path, file_name))
                else:
                    found.append(file_name)
    else:
        files = os.listdir(root_folder)
        for f in files:
            file_path = path.join_path(root_folder, f)
            if path.is_file(file_path=file_path):
                if full_path:
                    found.append(file_path)
                else:
                    found.append(f)

    return found


def get_files_and_folders(directory):
    """
    Get files and folders found in the given directory
    :param directory: str, folder we want to get files and folders from
    :return: list<str>
    """

    from tpPyUtils import path

    if not path.is_dir(directory=directory):
        return

    return os.listdir(directory)


def get_files_with_extension(extension, root_directory, full_path=False):
    """
    Returns file in given directory with given extensions
    :param extension: str, extension to find (.py, .data, etc)
    :param root_directory: str, directory path
    :param full_path: bool, Whether to return the file path or just the file names
    :return: list(str)
    """

    found = list()

    objs = os.listdir(root_directory)
    for filename_and_extension in objs:
        filename, found_extension = os.path.splitext(filename_and_extension)
        if found_extension == '.{}'.format(extension):
            if not full_path:
                found.append(filename_and_extension)
            else:
                found.append(os.path.join(root_directory, filename_and_extension))

    return found


def get_files_date_sorted(root_directory, extension=None):
    """
    Returns files date sorted found in the given directory
    :param root_directory: str, directory path
    :param extension: str, optional extension to find
    :return: list(str), list of files date sorted in the directory
    """

    if not extension:
        files = get_files(root_folder=root_directory)
    else:
        files = get_files_with_extension(extension=extension, root_directory=root_directory)

    mtime = lambda f: os.stat(os.path.join(root_directory, f)).st_mtime

    return list(sorted(files, key=mtime))


def open_folder(path=None):
    """
    Opens a folder in the explorer in a independent platform way
    If not path is passed the current directory will be opened
    :param path: str, folder path to open
    """

    if path is None:
        path = os.path.curdir
    if sys.platform == 'darwin':
        subprocess.check_call(['open', '--', path])
    elif sys.platform == 'linux2':
        subprocess.Popen(['xdg-open', path])
    elif sys.platform is 'windows' or 'win32' or 'win64':
        new_path = path.replace('/', '\\')
        try:
            subprocess.check_call(['explorer', new_path], shell=False)
        except Exception:
            pass


def get_user_folder(absolute=True):
    """
    Get path to the user folder
    :return: str, path to the user folder
    """

    from tpPyUtils import path

    if absolute:
        return path.clean_path(os.path.abspath(os.path.expanduser('~')))
    else:
        return path.clean_path(os.path.expanduser('~'))


def get_temp_folder():
    """
    Get the path to the temp folder
    :return: str, path to the temp folder
    """

    from tpPyUtils import path

    return path.clean_path(tempfile.gettempdir())


def get_current_working_directory():
    """
    Returns current working directory
    :return: str, path to the current working directory
    """

    return os.getcwd()


def get_folders_from_path(path):
    """
    Gets a list of sub folders in the given path
    :param path: str
    :return: list<str>
    """

    folders = list()
    while True:
        path, folder = os.path.split(path)
        if folder != '':
            folders.append(folder)
        else:
            if path != '':
                folders.append(path)
            break
    folders.reverse()

    return folders


def get_folders_date_sorted(root_folder):
    """
    Returns folder dates sorted found in the given root directory
    :param root_folder: str, directory path
    :return: list(str): list of folder date sorted in the directory
    """

    mtime = lambda f: os.stat(os.path.join(root_folder, f)).st_mtime
    return list(sorted(os.listdir(root_folder), key=mtime))
