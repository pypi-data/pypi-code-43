#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extract results from multiple files into pandas data frames.

This module takes in file path expressions and extracts each of the matching
file paths matching into a pandas data frame.

The data frames are appended together into a single result, with additional
columns that contain the variables used in the file path expressions to identify
each of the matching files.

"""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


# pylint: disable=no-name-in-module,import-error
from sciexp2.common import utils
from sciexp2.common.filter import Filter


# pylint: disable=redefined-builtin
def extract(template, function, filter=None, path="_PATH_"):
    """Extract data from all files matching `template` and `filter`.

    Parameters
    ----------
    template : str
        Template for file paths to extract.
    function : callable
        Function returning a pandas data frame from a single file.
    filter : str or Filter, optional
        Filter for the set of path names extracted from `template`. Can
        reference any variable name in `template` as well as the one in `path`.
    path : str, optional
        Variable name used to hold each path name extracted from `template` when
        finding the files (see `sciexp2.common.utils.find_files`).

    Returns
    -------
    pandas.DataFrame or None
        Pandas data frame with the data from all files matching `template` and
        `filter`. Variables in `template` are added as new columns into the
        result (with their respective values on each row). If no file is found
        matching `template` and `filter`, returns `None`.

    Notes
    -----
    Argument `function` is called with a single argument, corresponding to one
    of the file path names matching `template` and `filter`.

    """
    filter_ = filter
    if filter_ is None:
        filter_ = Filter()
    else:
        filter_ = Filter(filter_)
    result = None

    files = utils.find_files(template, path=path)
    for elem in files:
        if not filter_.match(elem):
            continue

        elem_path = elem.pop(path)
        data = function(elem_path)
        data = data.assign(**elem)

        if result is None:
            result = data
        else:
            result = result.append(data, ignore_index=True)

    return result
