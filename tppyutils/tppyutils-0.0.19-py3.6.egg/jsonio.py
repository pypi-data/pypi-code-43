#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility methods related to write/read json files
"""


from __future__ import print_function, division, absolute_import

import json
import os

import tpPyUtils


def write_to_file(data, filename):

    """
    Writes data to JSON file
    """

    if '.json' not in filename:
        filename += '.json'

    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    return filename


def read_file(filename):

    """
    Get data from JSON file
    """

    if os.stat(filename).st_size == 0:
        return None
    else:
        try:
            with open(filename, 'r') as json_file:
                return json.load(json_file)
        except Exception as e:
            tpPyUtils.logger.warning('Could not read {0}'.format(filename))
            tpPyUtils.logger.warning(str(e))
