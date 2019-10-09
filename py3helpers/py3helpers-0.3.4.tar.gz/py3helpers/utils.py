#!/usr/bin/env python
"""Utility functions and classes for python"""
########################################################################
# File: utils.py
#  executable: utils.py
#
# Author: Andrew Bailey
# History: 12/09/17 Created
########################################################################

import logging
import os
import string
import random
import re
import json
import tarfile
from datetime import datetime
from contextlib import contextmanager
from io import StringIO
import sys
import numpy as np
import datetime
from collections import defaultdict
from itertools import takewhile, repeat, islice


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def create_logger(file_path, name="a", info=False, debug=False):
    """Create a logger instance which will write all logs to file path and display logs at requested level
    :param file_path: path to file without .log extension
    :param name: unique name of logger
    :param info: set logging level to INFO
    :param debug: set logging level to DEBUG
    :return: logger which will write all log calls to file and display at level requested
    """
    assert type(info) is bool, "info should be bool, you passed {}".format(type(info))
    assert type(debug) is bool, "debug should be bool, you passed {}".format(type(debug))
    assert type(file_path) is str, "file path needs to be string"
    assert type(name) is str, "name needs to be string"

    level = logging.WARNING
    if debug:
        level = logging.DEBUG
    if info:
        level = logging.INFO
    # create name for logger
    root_logger = logging.getLogger(name)
    root_logger.setLevel(logging.DEBUG)
    # format log info formatting
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s")

    file_handler = logging.FileHandler("{}.log".format(file_path))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(level)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return logging.getLogger(name)


def create_dot_dict(dictionary):
    """Creates a dot.dictionary object and searches for internal dictionaries and turns them into dot.dictionaries

    note: only searches dictionaries and lists. sets or other iterable objects are not changed

    :param dictionary: a dictionary
    """
    # initialize dot.dict
    dictionary = DotDict(dictionary)
    # check if we need to change values within dictionary
    for key, value in dictionary.items():
        if isinstance(value, dict):
            dictionary[key] = create_dot_dict(value)
        if isinstance(value, list):
            new_list = []
            for x in value:
                if isinstance(x, dict):
                    new_list.append(create_dot_dict(x))
                else:
                    new_list.append(x)
            dictionary[key] = new_list

    return dictionary


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dictionary):
        """dot.notation access to dictionary attributes for string keys ONLY!

        :param dictionary: a dictionary"""
        super(DotDict, self).__init__(dictionary)
        for key, value in dictionary.items():
            assert type(key) is str, "Key must be a string"


def list_dir(path, ext="", include_dirs=False):
    """get all file paths from local directory with extension
    :param ext: optional extension for file
    :param include_dirs: boolean option to include directories
    :param path: path to directory
    :return: list of paths to files
    """
    assert type(path) is str, "Path must be a string"
    assert os.path.isdir(path), "Path does not exist: {}".format(path)
    if ext == "":
        if include_dirs:
            only_files = [os.path.join(os.path.abspath(path), f) for f in
                          os.listdir(path) if
                          os.path.exists(os.path.join(os.path.abspath(path), f))]
        else:
            only_files = [os.path.join(os.path.abspath(path), f) for f in
                          os.listdir(path) if
                          os.path.isfile(os.path.join(os.path.abspath(path), f))]
    else:
        only_files = [os.path.join(os.path.abspath(path), f) for f in
                      os.listdir(path) if
                      os.path.isfile(os.path.join(os.path.abspath(path), f))
                      if f.endswith(ext)]
    return only_files


def load_json(path):
    """Load a json file and make sure that path exists"""
    path = os.path.abspath(path)
    assert os.path.isfile(path), "Json file does not exist: {}".format(path)
    with open(path) as json_file:
        args = json.load(json_file)
    return args


def save_json(dict1, path):
    """Save a python object as a json file"""
    path = os.path.abspath(path)
    with open(path, 'w') as outfile:
        json.dump(dict1, outfile, indent=2)
    assert os.path.isfile(path)
    return path


def time_it(func, *args):
    """Very basic timing function
    :param func: callable function
    :param args: arguments to pass to function
    :return: object returned from function, time to complete
    """
    assert callable(func), "Function is not callable"
    start = datetime.datetime.now()
    something = func(*args)
    end = datetime.datetime.now()
    return something, (end - start).total_seconds()


def debug(verbose=False):
    """Method for setting log statements with verbose or not verbose"""
    assert type(verbose) is bool, "Verbose needs to be a boolean"
    if verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")
        logging.info("This should not print.")


def check_numpy_table(data, req_fields):
    """CHeck if numpy table has required columns, raises errors if it does not

    :param data: numpy array
    :param req_fields: required fields to be found in numpy array
    :return True if passes test
    """
    if not isinstance(data, np.ndarray):
        raise TypeError('Data is not ndarray.')
    if data.dtype.names is not None:
        if not set(req_fields).issubset(data.dtype.names):
            raise KeyError(
                'Read data does not contain required fields: {}, got {}.'.format(
                    req_fields, data.dtype.names
                )
            )
    else:
        raise KeyError("Read data does not contain required fields")
    return True


def merge_two_dicts(dict1, dict2):
    """Given two dicts, merge them into a new dict as a shallow copy.
    source: https://stackoverflow.com/questions/38987/
    how-to-merge-two-python-dictionaries-in-a-single-expression"""
    assert type(dict1) is dict or type(dict1) is DotDict, "Both arguments must be dictionaries: type(arg1) = {}".format(
        type(dict1))
    assert type(dict2) is dict or type(dict2) is DotDict, "Both arguments must be dictionaries: type(arg2) = {}".format(
        type(dict2))
    final = dict1.copy()
    final.update(dict2)
    return final


def merge_dicts(dicts):
    """Given a list of dicts, merge them into a new dict.

    :param dicts: list of dictionaries to merge together
    """
    assert type(dicts) is list, "Must past list of dictionaries"
    for dictionary in dicts:
        assert type(dictionary) is dict or type(dictionary) is DotDict, "Every itme in dictionary must be a dictionary"

    final = dicts[0].copy()
    for dictionary in dicts[1:]:
        final.update(dictionary)
    return final


class TimeStamp:
    def __init__(self):
        self.timestamp = 0
        self.date = 0

    def posix_timestamp(self):
        now = datetime.datetime.now()
        now = now.timestamp()
        self.timestamp = now
        return self.timestamp

    @staticmethod
    def get_posix_date(timestamp):
        return str(datetime.datetime.utcfromtimestamp(timestamp))

    @staticmethod
    def get_local_date(timestamp):
        return str(datetime.datetime.fromtimestamp(timestamp))

    @staticmethod
    def str_to_timestamp(date, date_format='%Y-%m-%d %H:%M:%S.%f'):
        """Get timestamp from posix date"""
        date2 = datetime.datetime.strptime(date, date_format)
        timestamp = date2.replace(tzinfo=datetime.timezone.utc).timestamp()
        return timestamp

    def posix_date(self):
        if self.timestamp == 0:
            self.posix_timestamp()
        self.date = datetime.datetime.utcfromtimestamp(self.timestamp)
        return str(self.date)


def change_np_field_type(np_struct_array, name, data_type):
    """Return a new array that is like the structured numpy array, but has additional fields.
    description looks like description=[('test', '<i8')]

    :param np_struct_array: structured numpy array
    :param name: name of field in np_struct_array to change dtype
    :param data_type: dtype to change into
    """
    assert np_struct_array.dtype.fields is not None, "Must be a structured numpy array"
    assert name in np_struct_array.dtype.fields, "Name must be a field in the structured numpy array"
    dtypes = []
    # find field to replace
    for field in np_struct_array.dtype.descr:
        if field[0] == name:
            dtypes.append((name, data_type))
        else:
            dtypes.append(field)
    # create new array and copy fields over
    new = np.zeros(np_struct_array.shape, dtype=dtypes)
    for name in np_struct_array.dtype.names:
        new[name] = np_struct_array[name]
    return new


def allLexicographicRecur(string, data, last, index):
    """Generator for all permutations of an alphabetically sorted string

    source: https://www.geeksforgeeks.org/print-all-permutations-with-repetition-of-characters/
    :param string: alphabetically sorted string
    :param data: list of characters
    :param last: length of string wanted to iterate
    :param index: current index to fix
    :return: generator of strings
    """
    length = len(string)

    # One by one fix all characters at the given index and
    # recur for the subsequent indexes
    for i in range(length):

        # Fix the ith character at index and if this is not
        # the last index then recursively call for higher
        # indexes
        data[index] = string[i]

        # If this is the last index then print the string
        # stored in data[]
        if index == last:
            yield ''.join(data)
        else:
            for x in allLexicographicRecur(string, data, last, index + 1):
                yield x


def all_string_permutations(string, length=None):
    """Generates all lexicographically sorted permutations of a string

    source: https://www.geeksforgeeks.org/print-all-permutations-with-repetition-of-characters/
    :param string: string to create all lexicographically sorted permutations of a string
    :param length: length of desired strings
    :return: generator of strings
    """
    if length is None:
        length = len(string)
    assert length > 0, "Cannot provide empty string or length under 1"

    # Create a temp array that will be used by
    # allLexicographicRecur()
    data = [""] * (length + 1)

    # Sort the input string so that we get all output strings in
    # lexicographically sorted order
    string = sorted(''.join(set(string)))

    # Now print all permutaions
    return allLexicographicRecur(string, data, length - 1, 0)


def get_random_string(length, chars=string.ascii_uppercase):
    """Get random strings with given characters and given length

    note: if duplicate characters given, they will not be removed. It is assumed that the user wants certain characters
            selected more frequently than other characters

    :param length: length of random string
    :param chars: chars to select randomly, default is all uppercase ascii chars.
    """
    return ''.join(random.choice(chars) for _ in range(length))


def get_random_strings(n_strings, len_string, chars=string.ascii_uppercase):
    """Generate N unique random strings given an alphabet and constant length of the string
    :param n_strings: number of strings to generate
    :param len_string: size of the strings
    :param chars: alphabet to work with
    """
    assert max_number_of_possible_strings(len_string, len(chars)) >= n_strings, \
        "Cannot generate this many random strings." \
        " max_n_possible_strings {} > n_strings {}".format(max_number_of_possible_strings(len_string, len(chars)),
                                                           n_strings)

    if max_number_of_possible_strings(len_string, len(chars)) / 2 <= n_strings:
        all_strings = np.random.choice([x for x in all_string_permutations(chars, len_string)], n_strings,
                                       replace=False)
    else:
        all_strings = set()
        while len(all_strings) < n_strings:
            all_strings |= {get_random_string(len_string, chars)}

    return list(all_strings)


def max_number_of_possible_strings(len_string, n_chars):
    return n_chars ** len_string


def find_substring_indices(main_string, sub_string, offset=0, overlap=True):
    """Generator that finds start positions of specific substring in a string, including overlapping substrings

    :param main_string: main_string to search
    :param sub_string: string to find instances of within the main_string
    :param offset: if you are searching for the index of an internal character of the substring we will add the
                    offset to the index. Default: 0
    :param overlap: boolean option if you want to find overlap eg.                Default: True
                    find_substring_indices("AAAA", "AA", overlap=True) = [0,1,2]
                    find_substring_indices("AAAA", "AA", overlap=False) = [0,2]

    :return: generator yielding (substring_start_index + offset)
    """
    assert len(sub_string) >= 1, "You must select a substring with len(sub_string) >= 1: {}".format(sub_string)
    assert len(main_string) >= 1, "You must select a main_string with len(main_string) >= 1: {}".format(main_string)
    if overlap:
        sub = '(?=(' + sub_string + "))"
    else:
        sub = sub_string
    for m in re.finditer(sub, main_string):
        yield m.start() + offset


def merge_lists(list_of_lists):
    """merge all items from a list of lists into a single list
    :param list_of_lists: a list of lists
    :return: a list with all elements from all lists
    """
    return [item for sublist in list_of_lists for item in sublist]


def count_lines_in_file(txt_file):
    """Count the lines in a text file

    source: https://stackoverflow.com/questions/845058/how-to-get-line-count-cheaply-in-python

    :param txt_file: path to text file of any type
    :return: number of lines in file
    """
    assert os.path.isfile(txt_file), "Input file is not a file. {}".format(txt_file)
    f = open(txt_file, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
    total = sum(buf.count(b'\n') for buf in bufgen)
    f.close()
    return total


def all_abspath(test_path):
    """Return original object if it is not string

    :param test_path: preferably a string object but will not error if non string object is passed
    """
    if type(test_path) is str:
        return os.path.abspath(test_path)
    else:
        return test_path


def split_every(n, iterable):
    """https://stackoverflow.com/questions/9475241/split-string-every-nth-character"""
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))


def split_every_string(n, string):
    """https://stackoverflow.com/questions/9475241/split-string-every-nth-character"""
    for x in split_every(n, string):
        yield "".join(x)


def list_dir_recursive(directory, ext=""):
    """Dive into directory and yield all files with given extension"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(ext):
                yield os.path.join(root, file)


def get_all_sub_directories(directory, hidden=False):
    """Get all sub directories from a parent directory"""
    for root, dirs, files in os.walk(directory):
        for dir1 in dirs:
            if not hidden:
                if not (dir1.startswith(".") or dir1.startswith("_")):
                    yield os.path.join(root, dir1)
            else:
                yield os.path.join(root, dir1)


def binary_search(sorted_list, target, exact_match=True):
    """Binary search through a sorted list of numbers for a target. If exact_match is set to true, it will only return
        if target is in sorted_list
    :param sorted_list:
    :param target:
    :param exact_match:
    :return: index of item or

    """
    min = 0
    max = len(sorted_list) - 1
    avg = int(np.round((min + max) / 2))
    if exact_match:
        def return_condition():
            return sorted_list[avg] == target
    else:
        def return_condition():
            if avg == min:
                if target < sorted_list[avg]:
                    return True
            if avg == max:
                if sorted_list[avg] < target:
                    return True
            else:
                return sorted_list[avg] < target < sorted_list[avg + 1]

    while min < max:
        if return_condition():
            return avg
        elif sorted_list[avg] < target:
            return avg + 1 + binary_search(sorted_list[avg + 1:], target, exact_match)
        else:
            return binary_search(sorted_list[:avg], target, exact_match)

    # avg may be a partial offset so no need to print it here
    # print "The location of the number in the array is", avg
    return avg


def tar_gz(source_dir, out_path, keep_structure=True):
    """Create a tar file from a directory of files
    :param source_dir: path to directory to tar gz
    :param out_path: path to output file or directory
    :param keep_structure: keep directory structure
    """
    assert os.path.isdir(source_dir), "Source directory must be a directory: {}".format(source_dir)
    if keep_structure:
        arcname = os.path.basename(source_dir)
    else:
        arcname = None

    if os.path.isdir(out_path):
        out_path = os.path.join(out_path, os.path.basename(source_dir)+".tar.gz")

    with tarfile.open(out_path, "w:gz") as tar:
        tar.add(source_dir, arcname=arcname)

    return out_path


def untar_gz(tar_gz_file, out_dir="."):
    """Create a tar file from a directory of files
    :param tar_gz_file: tar.gz file to untar and unzip
    :param out_dir: path to directory to unpack tar file
    """
    tar = tarfile.open(tar_gz_file, "r:gz")
    tar.extractall(path=out_dir)
    tar.close()
    return out_dir


def convert_seconds(seconds):
    """Convert seconds into """
    seconds_in_day = 86400
    seconds_in_hr = 3600
    seconds_in_min = 60
    days = seconds // seconds_in_day
    hrs = (seconds - (days*seconds_in_day)) // seconds_in_hr
    mins = (seconds - (days*seconds_in_day) - (hrs*seconds_in_hr)) // seconds_in_min
    secs = (seconds - (days*seconds_in_day) - (hrs*seconds_in_hr) - (mins*seconds_in_min)) // 1
    return days, hrs, mins, secs


class NestedDefaultDict(defaultdict):
    """Create an infinitely deep default dictionary.

    source: https://stackoverflow.com/questions/19189274/nested-defaultdict-of-defaultdict
    """
    def __init__(self):
        super(NestedDefaultDict, self).__init__(NestedDefaultDict)

    def __repr__(self):
        return repr(dict(self))


if __name__ == '__main__':
    print("This is a library of python functions")
