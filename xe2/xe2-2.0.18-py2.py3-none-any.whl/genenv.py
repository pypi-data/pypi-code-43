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
# standard object to wrap the context of the generation
###############################################################################
import logging
import jinja2

import pymdtools.translate as translate
import pymdtools.mdtopdf as mdtopdf

import xe2layout.config as config

from . import resource

###############################################################################
# small function for debug in jinja (it s a filter)
###############################################################################
def print_to_console(txt):
    print(txt)
    return ''

###############################################################################
# small function for debug in jinja (it s a filter)
###############################################################################
def md_to_html(txt_md):
    convert = mdtopdf.get_md_to_html_converter('mistune')
    return convert(txt_md)

###############################################################################
# Get the default jinja2 environment
#
# @return the default jinja env
###############################################################################
def get_default_jinja_env(template_paths_conf):
    result = jinja2.Environment(
        loader=jinja2.FileSystemLoader(
            [template_paths_conf['jinja'], template_paths_conf['template']]),
        autoescape=jinja2.select_autoescape(['html', 'xml']))

    result.filters['debug'] = print_to_console
    result.filters['markdown'] = md_to_html

    return result

###############################################################################
# An object to manage the generation environment
###############################################################################
class GenerationEnvironment:
    def __init__(self, template_conf_filename):
        template_conf = config.read_yaml(template_conf_filename)

        self.__template_conf = template_conf
        self.__jinja_env = get_default_jinja_env(template_conf['paths'])
        self.__context = config.read_yaml(
            template_conf['paths']['context_filename'])
        self.__resources = resource.ResourceGroup(
            template_conf['paths']['resources'])
        self.__resources.add_files()

        self.__context[template_conf['lib_image_tag']] = \
            self.__resources.build_lib(template_conf['lib_image_ext'])

        self.__gettext_module_name = template_conf['gettext_module_name']
        self.__language_list = template_conf['language_list']
        self.__locale_folder = template_conf['paths']['locale']
        self.__init_translation()

    ###########################################################################
    # translation initialisation
    ###########################################################################
    def __init_translation(self):
        # search the locale dir
        translate.get_localedir(
            self.__gettext_module_name, self.__locale_folder)
        # init lang
        for lang in self.__language_list:
            logging.debug("Init lang = %s", lang)
            translate.get_translation(lang, self.__gettext_module_name,
                                      self.__locale_folder)

    ###########################################################################
    # Translate
    # @param obj the object to translate
    # @param lang the language
    # @return the object translated
    ###########################################################################
    def translate(self, obj, lang):
        return translate.translate(obj, lang, self.__gettext_module_name)

    ###########################################################################
    # Translate
    # @param obj the object to translate
    # @param lang the language
    # @return the object translated
    ###########################################################################
    def context_translated(self, lang, context=None):
        def translate_str(element):
            element = element.strip()
            if not element.startswith('_(') or not element.endswith(')'):
                return element
            return self.translate(element[3:-2], lang)

        def translate_obj(obj):
            if isinstance(obj, dict):
                return translate_dict(obj)
            if isinstance(obj, list):
                return translate_list(obj)
            if isinstance(obj, str):
                return translate_str(obj)
            return obj

        def translate_list(obj):
            result = []
            for key in obj:
                result.append(translate_obj(key))
            return result

        def translate_dict(obj):
            result = {}
            for key in obj:
                result[key] = translate_obj(obj[key])
            return result

        if context is not None:
            return translate_obj(context)

        return translate_obj(self.context)

    ###########################################################################
    # the context environment
    # @return the value
    ###########################################################################
    @property
    def resources(self):
        return self.__resources

    ###########################################################################
    # the context environment
    # @return the value
    ###########################################################################
    @property
    def context(self):
        return self.__context

    ###########################################################################
    # the jinja2 environment
    # @return the value
    ###########################################################################
    @property
    def jinja_env(self):
        return self.__jinja_env

    ###########################################################################
    # the jinja2 environment
    # @return the value
    ###########################################################################
    @property
    def template_conf(self):
        return self.__template_conf

    ###########################################################################
    # the jinja2 environment
    # @param value The value to set
    ###########################################################################
    @jinja_env.setter
    def jinja_env(self, value):
        self.__jinja_env = value

    ###########################################################################
    # __str__ is a built-in function that computes the "informal"
    # string reputation of an object
    # __str__ goal is to be readable
    ###########################################################################
    def __str__(self):
        result = ""
        result += "-- Resources -------------------------------------------\n"
        result += str(self.__resources)
        result += "-- End Resources ---------------------------------------\n"

        result += "-- Context ---------------------------------------------\n"
        for key in self.__context:
            result += "%20s=%s\n" % (key, self.__context[key])
        result += "-- End Context -----------------------------------------\n"

        return result
