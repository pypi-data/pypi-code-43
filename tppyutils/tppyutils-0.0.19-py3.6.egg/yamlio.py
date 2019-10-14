#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Utility methods related to write/read YAML files
"""


from __future__ import print_function, division, absolute_import

import os
import yaml

import tpPyUtils


def write_to_file(data, filename):

    """
    Writes data to JSON file
    """

    if '.yml' not in filename:
        filename += '.yml'

    with open(filename, 'w') as yaml_file:
        yaml.dump(data, yaml_file)

    return filename


def read_file(filename):

    """
    Get data from JSON file
    """

    if os.stat(filename).st_size == 0:
        return None
    else:
        try:
            with open(filename, 'r') as yaml_file:
                return yaml.safe_load(yaml_file)
        except Exception as e:
            tpPyUtils.logger.warning('Could not read {0}'.format(filename))
            tpPyUtils.logger.warning(str(e))
