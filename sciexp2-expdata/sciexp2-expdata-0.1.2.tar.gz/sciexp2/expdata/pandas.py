#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


from sciexp2.common import utils


def extract(template, function, *args, **kwargs):
    """Extract data from all files matching `template` as a pandas data frame.

    Parameters
    ----------
    template : str
        Template for file paths to extract.
    function : callable
        Function returning a pandas data frame from a single file (path passed
        as first argument).
    args, kwargs
        Additional arguments to `function`.

    Returns
    -------
    pandas.DataFrame
        Pandas data frame with the data from all files matching `template`. The
        variables referenced in `template` are added as new columns into the
        result (with their respective values on each row).

    """
    result = None
    files = utils.find_files(template, path="PATH")
    for elem in files:
        path = elem.pop("PATH")
        data = function(path, *args, **kwargs)
        data = data.assign(**elem)

        if result is None:
            result = data
        else:
            result = result.append(data, ignore_index=True)

    return result
