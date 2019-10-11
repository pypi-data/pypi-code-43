__all__ = ['get_file_abspath', 'get_filename', 'touch']

import os


def get_file_abspath(file):
    location = os.path.realpath(os.path.dirname(__file__))
    path = os.path.join(location, file)
    return path


def get_filename():
    from sys import argv
    # getting filename
    filename = os.path.basename(argv[0])
    # if file has dots in name
    tmp_list = filename.split('.')
    if len(tmp_list) > 1:
        tmp_list.pop(-1)
        filename = '.'.join(tmp_list)
    return filename


def touch(file):
    with open(file, 'a'):
        os.utime(file, None)
