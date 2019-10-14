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
# Function to generate a page
###############################################################################

import collections
from copy import deepcopy
import htmlmin.decorator
from pymdtools import mistunege as mistune

from . import renderer

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
def dict_merge(dct, merge_dct, add_keys=True):
    dct = deepcopy(dct)

    if not add_keys:
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }

    for k, value in merge_dct.items():
        if isinstance(dct.get(k), dict) \
           and isinstance(value, collections.Mapping):
            dct[k] = dict_merge(dct[k], value, add_keys=add_keys)
        else:
            dct[k] = value
    return dct


###############################################################################
# Generate page content
###############################################################################
def generate_content(page_obj, genenv_obj, site_context=None):
    the_context = page_obj.context
    lib_image_tag = genenv_obj.template_conf['lib_image_tag']
    the_context[lib_image_tag] = genenv_obj.context[lib_image_tag]
    if site_context is not None and 'www_root_path' in site_context:
        the_context['www_root_path'] = site_context['www_root_path']
    if site_context is not None and 'res_root_path' in site_context:
        the_context['res_root_path'] = site_context['res_root_path']

    my_renderer = renderer.RendererDispatch(jinja_env=genenv_obj.jinja_env,
                                            context=page_obj.context)
    html_converter = mistune.Markdown(renderer=my_renderer)

    result = html_converter(page_obj.content)

    return result

###############################################################################
# Generate page content
###############################################################################
# @htmlmin.decorator.htmlmin(remove_comments=True)
def generate_page(page_obj, genenv_obj, site_context=None):
    lang = 'fr'
    if 'lang' in genenv_obj.context:
        lang = genenv_obj.context['lang']
    if site_context is not None and 'lang' in site_context:
        lang = site_context['lang']

    # template context
    the_context = genenv_obj.context_translated(lang)

    # override with the site context
    if site_context is not None:
        the_context = dict_merge(the_context, site_context)

    # override with the page context from the page
    the_context = dict_merge(the_context, page_obj.page_context)

    # generate the main content
    the_context['content'] = generate_content(page_obj, genenv_obj,
                                              site_context)

    the_template = genenv_obj.jinja_env.get_template("main_page.html")

    return the_template.render(the_context)
