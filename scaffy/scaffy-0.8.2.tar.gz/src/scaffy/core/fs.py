# -*- coding: utf-8 -*-
""" File system related helpers. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import re
import os
import fnmatch
from os.path import join, isdir, normpath


def filtered_walk(path, exclude):
    """ Walk recursively starting at *path* excluding files matching *exclude*

    :param str path:
        A starting path. This has to be an existing directory.
    :param List[str] exclude:
        A list of glob string patterns to test against. If the file/path
        matches any of those patters, it will be filtered out.
    :return:
        A generator yielding all the files that do not match any pattern in
        *exclude*.
    """
    if not isdir(path):
        raise ValueError("Cannot walk files, only directories")

    files = os.listdir(path)
    for name in files:
        file_path = normpath(join(path, name))

        if is_excluded(file_path, exclude):
            continue

        yield file_path

        if isdir(file_path):
            for p in filtered_walk(file_path, exclude):
                yield p


def is_excluded(path, excluded):
    """ Test whether the given *path* matches any patterns in *excluded*

    :param str path:
        A file path to test for matches.
    :param List[str] excluded:
        A list of glob string patterns to test against. If *path* matches any
        of those patters, it will return True.
    :return bool:
        True if the *path* matches any pattern in *excluded*.
    """
    for pattern in (p for p in excluded if p):
        if pattern.startswith('/'):
            # If pattern starts with root it means it match from root only
            regex = fnmatch.translate(pattern[1:])
            m = re.search(regex, path)

            if m and m.start == 0:
                return True

        else:
            regex = fnmatch.translate(pattern)
            if re.search(regex, path):
                return True

    return False
