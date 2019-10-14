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
# standard object to wrap file and access easily to the filename
# dark grey light
###############################################################################

import logging
import sys
import os
import os.path

from pymdtools.mdfile import MarkdownContent
import pymdtools.common as common
import pymdtools.mdcommon as mdcommon
import pymdtools.mdtopdf as mdtopdf
import pymdtools.mistunege as mistune

###############################################################################
# An object to rule the web page (only one page)
###############################################################################
class Page:

    ###########################################################################
    # Initialize the object from a content a filename or other
    #
    # @param filename the filename of the md file
    # @param encoding the encoding to read the file
    ###########################################################################
    def __init__(self, filename, encoding="utf-8"):
        self.__md = MarkdownContent(filename=filename, encoding=encoding)
        self.__context = {}
        self.__page_context = {}
        self.__site_context = {}
        self.read_context_from_md()

    ###########################################################################
    # the context environment
    # @return the value
    ###########################################################################
    @property
    def context(self):
        return self.__context

    ###########################################################################
    # the context environment
    # @return the value
    ###########################################################################
    @property
    def page_context(self):
        return self.__page_context

    ###########################################################################
    # the context environment
    # @return the value
    ###########################################################################
    @property
    def site_context(self):
        return self.__site_context

    ###########################################################################
    # Fill the context with the md content
    ###########################################################################
    def read_context_from_md(self):
        for key in self.__md:
            if key.startswith('site:'):
                self.__site_context[key[5:]] = self.__md[key]
                self.__site_context['site_' + key[5:]] = self.__md[key]
            elif key.startswith('page:'):
                self.__page_context[key[5:]] = self.__md[key]
                self.__page_context['page_' + key[5:]] = self.__md[key]
            else:
                self.__context[key] = self.__md[key]

    ###########################################################################
    # the markdown content
    # @return the content pf the marckdown
    ###########################################################################
    @property
    def content(self):
        return self.__md.content

    ###########################################################################
    # the jinja2 environment
    # @param value The value to set
    ###########################################################################
    @content.setter
    def content(self, value):
        self.__md.content = value

    ###########################################################################
    # the markdown content
    # @return the content pf the marckdown
    ###########################################################################
    @property
    def md_content(self):
        return self.__md

    ###########################################################################
    # Access to members by identifier
    # @return the list
    ###########################################################################
    def __getitem__(self, key):
        return self.__context[key]

    ###########################################################################
    # Access to members by identifier
    # @return the list
    ###########################################################################
    def __delitem__(self, key):
        if key in self.__context:
            del self.__context[key]

    ###########################################################################
    # Access to members by identifier
    # @return the list
    ###########################################################################
    def __setitem__(self, key, value):
        self.__context[key] = value

    ###########################################################################
    # test if a member is in the list
    # @return result of the test
    ###########################################################################
    def __contains__(self, key):
        return key in self.__context

    ###########################################################################
    # define iterator
    # @return the iterator
    ###########################################################################
    def __iter__(self):
        return self.__context.__iter__()

    ###########################################################################
    # Access to members
    # @return the length of the list
    ###########################################################################
    def __len__(self):
        return len(self.__context)

    ###########################################################################
    # Access to members
    # @return the length of the list
    ###########################################################################
    def __iadd__(self, other):
        for key in other:
            self.__setitem__(key, other[key])

    ###########################################################################
    # __repr__ is a built-in function used to compute the "official"
    # string reputation of an object
    # __repr__ goal is to be unambiguous
    ###########################################################################
    def __repr__(self):
        return self.__md.full_filename

    ###########################################################################
    # __str__ is a built-in function that computes the "informal"
    # string reputation of an object
    # __str__ goal is to be readable
    ###########################################################################
    def __str__(self):
        result = ""
        result += self.__md.__str__()
        result += "-- Site context ----------------------------------------\n"
        for key in self.__site_context:
            result += "%20s=%s\n" % (key, self.__site_context[key])
        result += "-- End Site context ------------------------------------\n"

        result += "-- Page context ----------------------------------------\n"
        for key in self.__page_context:
            result += "%20s=%s\n" % (key, self.__page_context[key])
        result += "-- End Page context ------------------------------------\n"

        result += "-- Context ---------------------------------------------\n"
        for key in self.__context:
            result += "%20s=%s\n" % (key, self.__context[key])
        result += "-- End Context -----------------------------------------\n"
        return result


###############################################################################
# Get the local folder of this script
#
# @return the local folder.
###############################################################################
def get_local_folder():
    return os.path.split(os.path.abspath(os.path.realpath(
        __get_this_filename())))[0]


###############################################################################
# Find the filename of this file (depend on the frozen or not)
# This function return the filename of this script.
# The function is complex for the frozen system
#
# @return the filename of THIS script.
###############################################################################
def __get_this_filename():
    result = ""

    if getattr(sys, 'frozen', False):
        # frozen
        result = sys.executable
    else:
        # unfrozen
        result = __file__

    return result


###############################################################################
# Set up the logging system
###############################################################################
def __set_logging_system():
    log_filename = os.path.splitext(os.path.abspath(
        os.path.realpath(__get_this_filename())))[0] + '.log'
    logging.basicConfig(filename=log_filename, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


###############################################################################
# Main script call only if this script is runned directly
###############################################################################
def __main():
    # ------------------------------------
    logging.info('Started %s', __get_this_filename())
    logging.info('The Python version is %s.%s.%s',
                 sys.version_info[0], sys.version_info[1], sys.version_info[2])

    num_ex = 4
    the_folder = os.path.join(get_local_folder(),
                              "../../examples/example%02d/" % num_ex)
    folder_input = os.path.join(the_folder, "input-md/")
    folder_output = os.path.join(the_folder, "output/")

    folder_output = common.check_create_folder(folder_output)

    resources = resource.ResourceGroup(
        os.path.join(get_local_folder(), "../../layout/template_resources/"))
    resources.add_files()
    resources.copy(folder_output)

    context = {}
    context['lib_image'] = resources.build_lib([".png", '.jpg'])
    # print(context['lib_image'])

    xxx = Page(os.path.join(folder_input, "index.md"), context=context)
    xxx.write(os.path.join(folder_output, "index.html"))

    # print(x.render())

    # create_footer(os.path.join(folder_input, 'footer.md'))
    # test_menu("menu_general.j2")

    logging.info('Finished')
    # ------------------------------------


###############################################################################
# Call main function if the script is main
# Exec only if this script is runned directly
###############################################################################
if __name__ == '__main__':
    __set_logging_system()
    __main()
