import os
import shutil
import hashlib


def ensure_folder(path):
    os.makedirs(path, exist_ok=True)
    return path


def clear_folder(path):
    """
    Given a folder, remove files and sub folders to make it empty.
    The given folder itself will not be deleted.

    :param path: The folder to be cleared.
    :return: The folder itself.
    """
    shutil.rmtree(path)
    ensure_folder(path)
    return path


def make_file_name(base_name, extension):
    return f"{base_name}.{extension}"


def make_full_path(parent_folder, base_name, extension):
    file_name_with_extension = make_file_name(base_name, extension)
    return os.path.join(parent_folder, file_name_with_extension)


def get_file_name(full_path):
    from pathlib import Path
    return Path(full_path).name


def iter_files(path, recursive=True, predicate=lambda _: True):
    """
    Given a path, iterate all files inside it.

    :param path: The folder from with to find files from.
    :param recursive: Find sub folders if True, else find only given folder.
    :param predicate: Find files only when this function evaluates `True` when file full path as the param.
    :return: A generator generates the files which file name meets `predicate`.
    """
    for cur_dir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(cur_dir, file)
            if predicate(full_path):
                yield full_path

        # break if non recursive
        if not recursive:
            break


def md5_file(f):
    h = hashlib.md5()
    with open(f, 'rb') as fin:
        h.update(fin.read())
    return h.hexdigest()


def is_xml_file(path):
    _, extension = os.path.splitext(path)
    return extension.lower() == '.xml'


def is_json_file(path):
    _, extension = os.path.splitext(path)
    return extension.lower() == '.json'


def iter_xml_files(path, recursive=True):
    yield from iter_files(path, recursive=recursive, predicate=is_xml_file)


def iter_json_files(path, recursive=True):
    yield from iter_files(path, recursive=recursive, predicate=is_json_file)


class ExecuteInDirectory:
    def __init__(self, file_path, is_directory=False):
        # The reason that explicitly pass a is_directory bool parameter
        # is os.path.isfile/os.path.isdir simply does't work well on Windows
        if is_directory:
            self.target_dir = file_path
            self.target_file_name = None
        else:
            self.target_dir = os.path.dirname(file_path)
            self.target_file_name = os.path.basename(file_path)

    def __enter__(self):
        self.backup_cwd = os.getcwd()
        os.chdir(self.target_dir)

        if self.target_file_name:
            return self.target_file_name

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.backup_cwd)
