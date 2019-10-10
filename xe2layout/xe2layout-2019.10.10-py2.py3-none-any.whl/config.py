#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# @copyright Copyright (C) Guichet Entreprises - All Rights Reserved
# 	All Rights Reserved.
# 	Unauthorized copying of this file, via any medium is strictly prohibited
# 	Dissemination of this information or reproduction of this material
# 	is strictly forbidden unless prior written permission is obtained
# 	from Guichet Entreprises.
###############################################################################

###############################################################################
# Some functions to red config files
###############################################################################
import logging
import os.path
import codecs
import collections
from copy import deepcopy
import yaml

import pymdtools.common


###############################################################################
# Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
# updating only top-level keys, dict_merge recurses down into dicts nested
# to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
# ``dct``.
#
# This version will return a copy of the dictionary and leave the original
#     arguments untouched.
#
# The optional argument ``add_keys``, determines whether keys which are
#     present in ``merge_dict`` but not ``dct`` should be included in the
#     new dict.
#
#
# Code from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
#
# Args:
#         dct (dict) onto which the merge is executed
#         merge_dct (dict): dct merged into dct
#         add_keys (bool): whether to add new keys
#
# Returns:
#         dict: updated dict
###############################################################################
def __dict_merge(dct, merge_dct, add_keys=True):
    dct = deepcopy(dct)

    if not add_keys:
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }

    for k, value in merge_dct.items():
        if isinstance(dct.get(k), dict) \
           and isinstance(value, collections.Mapping):
            dct[k] = __dict_merge(dct[k], value, add_keys=add_keys)
        else:
            dct[k] = value
    return dct


###############################################################################
# Compute an absolute path from the config parameter
#
# @param paths list of paths to compute
# @return the absolute path
###############################################################################
def path(*paths):
    result = ""
    for path_element in paths:
        if len(result) > 0:
            result = os.path.join(path_element, result)
        else:
            result = path_element
        if os.path.isabs(result):
            return os.path.normpath(pymdtools.common.set_correct_path(result))

    return os.path.normpath(pymdtools.common.set_correct_path(result))

###############################################################################
# Expand paths in the config file
#
# @param data the config part
# @param root the root of the config part
# @return the dict of the config
###############################################################################
def expand_paths(data, root):
    if 'root' not in data:
        data['root'] = './'

    # Set the root path absolute
    data['root'] = path(data['root'], root)

    for key in data:
        if isinstance(data[key], dict):
            data[key] = expand_paths(data[key], data['root'])
        elif isinstance(data[key], list):
            new_list = []
            for element in data[key]:
                new_list.append(path(element, data['root'], root))
            data[key] = new_list
        else:
            data[key] = path(data[key], data['root'], root)

    return data

###############################################################################
# Read conf yaml
#
# @param filename the config filename
# @return the dict of the config
###############################################################################
def __read_yaml(filename):
    logging.debug('Read the yaml config file %s', (filename))
    filename = pymdtools.common.check_is_file_and_correct_path(filename)
    filename_path = os.path.dirname(filename)
    with codecs.open(filename, "r", "utf-8") as ymlfile:
        result = yaml.load(ymlfile, Loader=yaml.FullLoader)

    logging.debug('Read finished for the yaml config file %s', (filename))

    if 'paths' not in result:
        return result

    includes_full = []
    if 'paths' in result and 'includes' in result['paths']:
        for inc_fn in result['paths']['includes']:
            inc_fn_full = os.path.join(filename_path, inc_fn)
            includes_full.append(inc_fn_full)
            with codecs.open(inc_fn_full, "r", "utf-8") as ymlfile:
                include_conf = yaml.load(ymlfile, Loader=yaml.FullLoader)
            result = __dict_merge(include_conf, result, add_keys=True)

    result['paths']['includes'] = includes_full

    logging.debug('Add some info in the config result for all paths')

    result['paths'] = expand_paths(result['paths'],
                                   os.path.split(filename)[0])

    if 'conf_folder' not in result['paths']:
        result['paths']['conf_folder'] = os.path.split(filename)[0]
    if 'conf_filename' not in result['paths']:
        result['paths']['conf_filename'] = filename

    return result

###############################################################################
# Read conf yaml
#
# @param filename the config filename
# @return the dict of the config
###############################################################################
def read_yaml(filename):
    logging.debug('Read the yaml config file %s', (filename))
    filename = pymdtools.common.check_is_file_and_correct_path(filename)
    result = __read_yaml(filename)

    (folder, loc_filename) = os.path.split(filename)
    (loc_filename, filename_ext) = os.path.splitext(loc_filename)

    local_filename = os.path.join(
        folder, loc_filename) + ".local" + filename_ext
    logging.debug("local_filename = %s", local_filename)

    if not os.path.isfile(local_filename):
        return result

    logging.debug('Read the yaml local config file %s', (local_filename))
    local_conf = __read_yaml(local_filename)
    result = __dict_merge(result, local_conf)

    return result

###############################################################################
# Write a yaml config conf yaml
#
# @param data the data to write
# @param filename the config filename
# @return empty
###############################################################################
def write_yaml(filename, data):
    filename = pymdtools.common.set_correct_path(filename)
    logging.debug('Write the yaml config file %s', (filename))
    stream = open(filename, 'w', encoding=('utf-8'))
    yaml.dump(data, stream,
              default_flow_style=False, encoding=('utf-8'),
              allow_unicode=True)
    stream.close()

    logging.debug('Write finished for the yaml config file %s', (filename))
