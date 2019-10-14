#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility methods related to write/read (IO) text files
"""


from __future__ import print_function, division, absolute_import


import os
import sys
import stat
import json
import string
import shutil
import getpass
import datetime
import subprocess
from tempfile import mkstemp
from shutil import move


# region Classes
class FileManager(object):
    """
    Base class to deal with file writing and reading
    """

    def __init__(self, file_path, skip_warning=False):
        """
        :param file_path: str, path to the file to work with
        :param skip_warning: bool, Whether to print warnings or not
        """

        self.file_path = file_path
        self.open_file = None

        if not skip_warning:
            self.check_path(warning_text='Path {} is invalid!'.format(file_path))

    # region Public Functions
    def get_open_file(self):
        """
        Returns managed file and opens it
        :return:  str
        """

        return self.open_file()

    def read_file(self):
        """
        Opens managed file to read
        """

        self.check_file(warning_text='File {} is invalid!'.format(self.file_path))
        self.open_file = open(self.file_path, 'r')

    def write_file(self):
        """
        Opens managed file to write data into (removing any previous data)
        """

        self.check_file(warning_text='File {} is invalid!'.format(self.file_path))
        self.open_file = open(self.file_path, 'w')

    def append_file(self):
        """
        Opens managed file to append data to the current file data
        """

        self.check_file(warning_text='File {} is invalid!'.format(self.file_path))
        self.open_file = open(self.file_path, 'a')

    def close_file(self):
        """
        Close managed file
        """

        if self.open_file:
            self.open_file.close()

    def check_folder(self, warning_text=None):
        """
        Check if a folder is an invalid one and raise error if necessary
        :param warning_text: str
        :return: bool
        """

        from tpPyUtils import path

        if not path.is_dir(self.file_path):
            if warning_text is not None:
                raise NameError(str(warning_text))
            return False

        return True

    def check_path(self, warning_text=None):
        """
        Check if a path to a file is invalid and raise error if necessary
        :param warning_text: str
        :return: bool
        """

        from tpPyUtils import path

        dir_name = path.get_dirname(self.file_path)

        if not path.is_dir(dir_name):
            if warning_text is not None:
                raise UserWarning(str(warning_text))
            return False

        return True

    def check_file(self, warning_text=None):
        """
        Check if a file is an invalid one and raise error if necessary
        :param warning_text: str
        :return: bool
        """

        from tpPyUtils import path

        if not path.is_file(self.file_path):
            if warning_text is not None:
                raise UserWarning(str(warning_text))
            return False

        return True
    # endregion


class FileReader(FileManager, object):
    """
    Class to deal with file read operations
    """

    def __init__(self, file_path):
        super(FileReader, self).__init__(file_path=file_path)

    # region Public Functions
    def read(self):
        """
        Read managed file
        :return: list<str>, list of file lines
        """

        self.read_file()
        lines = self._get_lines()
        self.close_file()

        return lines
    # endregion

    # region Private Functions
    def _get_lines(self):
        try:
            lines = self.open_file.read()
        except:
            return []

        return get_text_lines(lines)


class FileWriter(FileManager, object):
    """
    Class to deal with file write operations
    """

    def __init__(self, file_path):
        super(FileWriter, self).__init__(file_path=file_path)

        from tpPyUtils import osplatform

        osplatform.get_permission(file_path)
        self.append = False

    # region Override Functions
    def write_file(self):
        """
        Overrides write file. This function creates the file if it does not exists
        If append is True, then append any lines to the file instead or replacing
        """

        if self.append:
            self.append_file()
        else:
            super(FileWriter, self).write_file()
    # endregion

    # region Public Functions
    def set_append(self, append):
        """
        If True, next write operations will append new lines to end of documents otherwise the text
        content will be replaced entirely
        :param append: bool
        """

        self.append = append

    def write_line(self, line):
        """
        Writes a single line to the file and closes managed file after write operation
        :param line: str, line to add to the file
        """

        self.write_file()
        try:
            self.open_file.write('%s\n' % line)
        except Exception:
            pass
        self.close_file()

    def write_json(self, dict_data):
        """
        Writes given JSON data (dict) into file
        :param dict_data: dict
        """

        self.write_file()
        try:
            json.dump(dict_data, self.open_file, indent=4, sort_keys=True)
        except Exception:
            pass
        self.close_file()

    def write(self, lines, last_line_empty=True):
        """
        Write the given list of lines to the managed file
        :param lines: list<str>, list of lines to write to the managed file
        :param last_line_empty: bool, whether or not to add a line after the last line
        """

        self.write_file()

        try:
            inc = 0
            for line in lines:
                if inc == len(lines)-1 and not last_line_empty:
                    self.open_file.write(str('%s' % line))
                    break
                self.open_file.write(str('%s\n' % line))
                inc += 1
        except Exception:
            print('Could not write to file {}'.format(self.file_path))

        self.close_file()
    # endregion


class FileVersion(object):
    """
    Utility class to version files or folders
    """

    def __init__(self, file_path):

        from tpPyUtils import path

        self.file_path = file_path
        if file_path:
            self.filename = path.get_basename(directory=self.file_path)
            self._path = path.get_dirname(file_path)
            self._version_folder_name = '__version__'
            self._version_name = 'version'
            self._version_folder = None
            self.comment_file = None
            self.updated_old = False

    # region Properties
    def get_version_name(self):
        return self._version_name

    def set_version_name(self, version_name):
        self._version_name = version_name

    def get_version_folder_name(self):
        return self._version_folder_name

    def set_version_folder_name(self, version_folder_name):
        self._version_folder_name = version_folder_name

    def get_version_folder(self):
        return self._version_folder

    def set_version_folder(self, version_folder):
        self._version_folder = version_folder


    version_name = property(get_version_name, set_version_name)
    version_folder_name = property(get_version_folder_name, set_version_folder_name)
    version_folder = property(get_version_folder, set_version_folder)
    # endregion

    # region Public Functions
    def has_versions(self):
        """
        Returns whether the version file already has versions folder created or not
        :return: bool
        """

        from tpPyUtils import path

        version_folder = self._get_version_folder()
        if path.is_dir(version_folder):
            return True

    def get_latest_version(self):
        """
        Returns the file path to the latest version
        :return: str
        """

        from tpPyUtils import path

        versions = self.get_versions()
        latest_version = versions[-1]

        return path.join_path(self.file_path, '{0}/{1}'.format(self.version_folder_name, latest_version))

    def get_versions(self, return_version_numbers_also=False):
        """
        Get file paths of all version
        :param return_version_numbers_also: Whether the number of the versions should be returned also
        :return: list
        """

        from tpPyUtils import folder, sort

        version_folder = self._get_version_folder()
        files = folder.get_files_and_folders(directory=version_folder)
        if not files:
            return None

        number_list = list()
        pass_files = list()

        for file_path in files:
            if not file_path.startswith(self.version_name):
                continue
            split_name = file_path.split('.')
            if not len(split_name) == 2:
                continue

            number = int(split_name[1])
            number_list.append(number)
            pass_files.append(file_path)

        if not pass_files:
            return

        quick_sort = sort.QuickNumbersListSort(list_of_numbers=number_list)
        quick_sort.set_follower_list(pass_files)
        pass_files = quick_sort.run()

        pass_dict = dict()
        for i in range(len(number_list)):
            pass_dict[pass_files[0][i]] = pass_files[1][i]

        if not return_version_numbers_also:
            return pass_dict
        else:
            return pass_dict, pass_files[0]

    def get_version_numbers(self):
        """
        Return file version numbers of all versions
        :return: list<int>, list of version numbers
        """

        from tpPyUtils import folder

        version_folder = self._get_version_folder()
        files = folder.get_files_and_folders(directory=version_folder)
        if not files:
            return

        number_list = list()
        for file_path in files:
            if not file_path.startswith(self.version_name):
                continue
            split_name = file_path.split('.')
            if not len(split_name) == 2:
                continue
            num = int(split_name[1])
            number_list.append(num)

        return number_list

    def save_comment(self, comment=None, version_file=None):
        """
        Saves a comment to the version file
        :param comment: str, commend to add to the version file
        :param version_file: str, version file
        """

        version = version_file.split('.')
        if version:
            version = version[-1]

        user = getpass.getuser()

        if not comment:
            comment = '-'
        comment.replace('"', '\"')

        comment_file = FileWriter(file_path=self.comment_file)
        comment_file.set_append(True)
        comment_file.write(['version = {0}; comment = "{1}"; user = "{2}"'.format(version, comment, user)])
        comment_file.close_file()

    def save(self, comment=None):
        """
        Saves a new version file
        :param comment: str
        :return: str, new version file name
        """

        from tpPyUtils import folder, path

        if not comment:
            comment = '-'
        comment.replace('\n', '   ')
        comment.replace('\r', '   ')

        self._create_version_folder()
        self._create_comment_file()

        unique_file_name = self._increment_version_file_name()

        if path.is_dir(self.file_path):
            folder.copy_folder(directory=self.file_path, directory_destination=unique_file_name)
        elif path.is_file(self.file_path):
            copy_file(file_path=self.file_path, file_path_destination=unique_file_name)

        self.save_comment(comment=comment, version_file=unique_file_name)

        return unique_file_name

    def get_version_data(self, version_number):
        """
        Returns the version data (comment and user) of the given version number
        :param version_number: int, version number
        :return: list<str, str>, tuple with comment and user of the given version
        """

        from tpPyUtils import path

        file_path = self._get_comment_path()
        if not file_path:
            return None, None

        if path.is_file(file_path):
            read = FileReader(file_path=file_path)
            lines = read.read()

            version = None
            comment = None
            user = None

            for line in lines:
                start_index = line.find('"')
                if start_index > -1:
                    end_index = line.find(';')
                    sub_part = line[start_index+1:end_index]
                    sub_part = sub_part.replace('"', '\\"')
                    line = line[:start_index+1] + sub_part + line[end_index:]

                try:
                    exec(line)
                except:
                    pass

                if version == version_number:
                    return comment, user

        return None, None

    def get_all_versions_data(self):
        """
        Returns all the version data (comment, user, file_size, modified and version_file) of all the versions
        :return: list<str, str, str, str, str, str>, tuple with version, comment, user, file_size, modified, version_file
        """

        from tpPyUtils import path

        versions = self.get_versions(return_version_numbers_also=True)
        if not versions:
            return
        else:
            version_paths = versions[0]
            version_numbers = versions[1]

        file_path = self._get_comment_path()
        if not file_path:
            return []

        datas = list()
        if path.is_file(file_path):
            read = FileReader(file_path)
            lines = read.read()
            for line in lines:
                line_info_dict = dict()
                version = None
                comment = None
                user = None
                file_size = None
                modified = None

                split_line = line.split(';')
                for sub_line in split_line:
                    assigment = sub_line.split('=')
                    if assigment and assigment[0]:
                        name = assigment[0].strip()
                        value = assigment[1].strip()
                        line_info_dict[name] = value

                # Version
                if not line_info_dict.has_key('version'):
                    continue
                version = int(line_info_dict['version'])
                if not version in version_numbers:
                    continue

                # Comment
                if line_info_dict.has_key('comment'):
                    comment = line_info_dict['comment']
                    comment = comment[1:-1]

                # User
                if line_info_dict.has_key('user'):
                    user = line_info_dict['user']
                    user = user[1:-1]

                # Version File
                version_file = version_paths[(version)]
                version_file = path.join_path(self.file_path, '{0}/{1}'.format(self.version_folder_name, version_file))

                # File Size
                file_size = get_file_size(file_path=version_file)

                # Modified
                modified = get_last_modified_date(file_path=version_file)

                datas.append([version, comment, user, file_size, modified, version_file])

        return datas

    def get_version_path(self, version_number):
        """
        Returns the path to the given version number
        :param version_number: int, version number
        :return: str, path to the version
        """

        return self._get_version_path(version_number=version_number)

    def get_version_comment(self, version_number):
        """
        Returns the comment of the given version number
        :param version_number: int, version number
        :return:  str, version_number comment
        """

        comment, user = self.get_version_data(version_number)
        return comment

    # endregion

    # region Private Functions
    def _get_version_folder(self):
        from tpPyUtils import path

        if path.is_file(self.file_path):
            dir_name = path.get_dirname(self.file_path)
            version_path = path.join_path(dir_name, self._version_folder_name)
        else:
            version_path = path.join_path(self.file_path, self._version_folder_name)

        return version_path

    def _get_version_path(self, version_number):
        from tpPyUtils import path
        return path.join_path(self._get_version_folder(), self._version_name + '.' + str(version_number))

    def _get_version_number(self, file_path):
        from tpPyUtils import name
        version_number = name.get_last_number(input_string=file_path)
        return version_number

    def _get_comment_path(self):
        from tpPyUtils import path
        version_folder = self._get_version_folder()
        file_path = None
        if version_folder:
            file_path = path.join_path(version_folder, 'comments.txt')

        return file_path

    def _create_version_folder(self):
        from tpPyUtils import folder
        self._version_folder = folder.create_folder(name=self._version_folder_name, directory=self._path)

    def _create_comment_file(self):
        self.comment_file = create_file(filename='comments.txt', directory=self._version_folder)

    def _increment_version_file_name(self):
        from tpPyUtils import path
        version_path = path.join_path(self._version_folder, self._version_name + '.1')
        return path.unique_path_name(directory=version_path)
    # endregion
# endregion


# region Functions
def open_browser(file_path):
    """
    Open the file browser to the path specified
    :param file_path: str, filename with path
    :return:
    """

    # TODO: Only work on Windows, make it cross platform

    from tpPyUtils import osplatform, path

    if not path.is_file(file_path) and not path.is_dir(file_path):
        return

    if osplatform.is_windows():
        os.startfile(file_path)
    elif osplatform.is_linux():
        try:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, file_path])
        except Exception as e:
            os.system('gnome-terminal --working-directory={}'.format(file_path))


def create_file(filename, directory, make_unique=False):
    """
    Creates a file
    :param filename: str, name of the new file
    :param directory: str, directory of the new file
    :param make_unique: bool, whether to make the name unique or not
    :return: variant, str || bool, filename with path or False if create file failed
    """

    from tpPyUtils import name, path

    filename = name.clean_file_string(filename)
    full_path = path.join_path(directory, filename)

    if make_unique:
        full_path = path.unique_path_name(full_path)

    try:
        open_file = open(full_path, 'a')
        open_file.close()
    except:
        return False

    return full_path


def copy_file(file_path, file_path_destination):
    """
    Copies the given file to a new given directory
    :param file_path: str, file to copy with full path
    :param file_path_destination: str, destination directory where we want to copy the file into
    :return: str, the new copied path
    """

    shutil.copy2(file_path, file_path_destination)
    return file_path_destination


def move_file(path1, path2):
    """
    Moves the file pointed by path1 under the directory path2
    :param path1: str, file with full path
    :param path2: str, path where path1 should be move into
    :return: bool, Whether the move operation was successfully
    """

    try:
        shutil.move(path1, path2)
    except:
        print('Failed to move {0} to {1}'.format(path1, path2))
        return False

    return True


def delete_file(name, directory):
    """
    Delete the file by name in the directory
    :param name: str, name of the file to delete
    :param directory: str, the directory where the file is stored
    :return: str, file path that was deleted
    """

    from tpPyUtils import path

    full_path = path.join_path(directory, name)
    if not path.is_file(full_path):
        return full_path

    os.chmod(full_path, 0o777)
    os.remove(full_path)

    return full_path


def rename_file(name, directory, new_name, new_version=False):
    """
    Renames the give nfile in the directory with a new name
    :param name:
    :param directory:
    :param new_name:
    :param new_version:
    :return:
    """

    from tpPyUtils import path

    full_path = path.join_path(directory, name)
    if not path.is_file(full_path):
        return full_path

    new_full_path = path.join_path(directory, new_name)
    if path.is_file(new_full_path):
        print('A file named {} already exists in the directory: {}'.format(new_name, directory))
        return full_path

    os.chmod(full_path, 0o777)
    os.rename(full_path, new_full_path)

    return new_full_path


def write_to_file(file_name, text_to_write):
    """
    Open a file and overwrite its contents of that file with new content
    """

    if os.path.exists(file_name):
        readOnlyOrWriteable = os.stat(file_name)[0]
        if readOnlyOrWriteable != stat.S_IWRITE:
            os.chmod(file_name, stat.S_IWRITE)
    file = open(file_name, 'w')
    file.write(text_to_write)
    file.close()


def append_to_file(file_name, text_to_add):
    """
    Open a file and add new context to its existing text
    """

    if os.path.exists(file_name):
        readOnlyOrWriteable = os.stat(file_name)[0]
        if readOnlyOrWriteable != stat.S_IWRITE:
            os.chmod(file_name, stat.S_IWRITE)
    file = open(file_name, 'a')
    file.write(text_to_add)
    file.close()


def replace(file_path, pattern, subst):
    """
    Replaces one string from another string in a given file
    :param file_path: str, path to the file
    :param pattern: search to be replaced
    :param subst: string that will replace the old one
    """

    #Create temp file
    fh, abs_path = mkstemp()
    with os.fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                # TODO: This gives when working with non ascii codecs, solve ethis without try/except
                try:
                    new_file.write(line.replace(pattern, subst))
                except:
                    pass
    #Remove original file
    os.remove(file_path)

    #Move new file
    move(abs_path, file_path)


def remove_extension(file_path):
    """
    Removes extension of the given file path
    For example, C:/test/rig.py will return rig
    :param file_path: str
    :return: str
    """

    split_path = file_path.split('.')
    new_name = file_path
    if len(split_path) > 1:
        new_name = string.join(split_path[:-1], '.')

    return new_name


def is_newer(file1, file2):
    """
    Returns true if file1 is newer than file2.
    :param str file1: first file to compare.
    :param str file2: second file to compare.
    :return: bool, True if file1 is newer or False otherwise
    """

    if not os.path.exists(file1) or not os.path.exists(file2):
        return False

    time1 = os.path.getmtime(file1)
    time2 = os.path.getmtime(file2)
    return time1 > time2


def is_file_in_dir(filename, directory):
    """
    Returns True if the given file name is contained in the given directory
    :param filename: str, file name
    :param directory: str, directory name including path
    :return: bool
    """

    from tpPyUtils import path

    file_path = path.join_path(directory, filename)
    return os.path.isfile(file_path)


def is_same_date(file1, file2):
    """
    Returns True if the given files have the same date
    :param file1: str, file name including path
    :param file2: str, file name including path
    :return: bool
    """

    date1 = os.path.getmtime(file1)
    date2 = os.path.getmtime(file2)
    value = date1 - date2
    if abs(value) < 0.01:
        return True

    return False


def get_file_text(file_path):
    """
    Get the text stored in a file in a unique string (without parsing)
    :param file_path: str
    :return: str
    """

    open_file = open(file_path, 'r')
    lines = ''

    try:
        lines = open_file.read()
        open_file.close()
    except Exception:
        open_file.close()

    return lines


def get_file_size(file_path, round_value=2):
    """
    Returns the size of the given file
    :param file_path: str
    :param round_value: int, value to round size to
    :return: str
    """

    size = os.path.getsize(file_path)
    size_format = round(size * 0.000001, round_value)

    return size_format


def get_size(file_path, round_value=2):
    """
    Return the size of the given directory or file path
    :param file_path: str
    :param round_value: int, value to round size to
    :return: int
    """

    from tpPyUtils import folder, path

    size = 0
    if path.is_dir(file_path):
        size = folder.get_folder_size(file_path, round_value)
    if path.is_file(file_path):
        size = get_file_size(file_path, round_value)

    return size


def get_last_modified_date(file_path):
    """
    Returns the last date given file was modified
    :param file_path: str
    :return: str, formated date and time
    """

    mtime = os.path.getatime(file_path)

    date_value = datetime.datetime.fromtimestamp(mtime)
    year = date_value.year
    month = date_value.month
    day = date_value.day

    hour = str(date_value.hour)
    minute = str(date_value.minute)
    second = str(int(date_value.second))

    if len(hour) == 1:
        hour = '0' + hour
    if len(minute) == 1:
        minute = '0' + minute
    if len(second) == 1:
        second = second + '0'

    return '{0}-{1}-{2}  {3}:{4}:{5}'.format(year, month, day, hour, minute, second)


def get_file_lines(file_path):
    """
    Get the text lines from a file
    :param file_path: str, file name of the text to read
    :return: str
    """

    reader = FileReader(file_path=file_path)
    return reader.read()


def get_text_lines(text):
    """
    Get all lines from a text storing each lines as a different item in a list
    :param text: str, text to get lines from
    :return: list<str>
    """

    text = text.replace('\r', '')
    lines = text.split('\n')

    return lines


def write_lines(file_path, lines, append=False):
    """
    Writes a list of text lines to a file. Every entry in the list is a new line
    :param file_path: str, filename and path
    :param lines: list<str>, list of text lines in which each entry is a new line
    :param append: bool, Whether to append the text or replace it
    """

    write_file = FileWriter(file_path=file_path)
    write_file.set_append(append)
    write_file.write(lines)
    write_file.close_file()


def is_same_text_content(file1, file2):
    """
    Returns True if the given text files contains the same text or False otherwise
    :param file1: str, file path to the first text
    :param file2: str, file path to the second text
    :return: bool
    """

    text1 = get_file_text(file_path=file1)
    text2 = get_file_text(file_path=file2)
    if text1 == text2:
        return True

    return False


def get_files(root_directory):
    """
    Returns files found in the given directorys
    :param root_directory: str
    :return: list(str)
    """

    found = list()

    files = os.listdir(root_directory)
    for filename in files:
        file_path = os.path.join(root_directory, filename)
        if os.path.isfile(file_path):
            found.append(filename)

    return found


def file_has_info(file_path):
    """
    Check if the given file size is bigger than 1.0 byte
    :param file_path: str, ful file path of the file to check
    :return: bool
    """

    file_stats = os.stat(file_path)
    if file_stats.st_size < 1:
        return False

    return True
