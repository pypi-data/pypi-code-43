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
#
###############################################################################

import logging
import os
import os.path
import re
import copy
import md2py

import pymdtools.common as common
import pymdtools.mdcommon as mdcommon
import pymdtools.mdfile as mdfile
import pymdtools.markdownify as markdownify
import pymdtools.instruction

__include_menu_re__ = \
    r"^(?P<level>[#]+)\s*<!--\s*include\((?P<name>[^)]+)\).*-->\s*"
__include_dir_re__ = \
    r"^(?P<level>[#]+)\s*<!--\s*dir\((?P<name>[^)]+)\).*-->\s*"

###############################################################################
# An object to set the menu List of Entry
###############################################################################
def create_menu_from_folder(folder, base_path):
    folder = common.set_correct_path(folder)
    result = ""
    for the_file in os.listdir(folder):
        the_file_full = os.path.join(folder, the_file)
        if os.path.isdir(the_file_full):
            result += "# %s\n" % the_file
            submenu = create_menu_from_folder(the_file_full, base_path)
            result += re.sub("^#", "##", submenu, flags=re.MULTILINE)
        elif the_file.lower().endswith(".md"):
            md_content = mdfile.MarkdownContent(the_file_full)
            path_to_file = os.path.relpath(the_file_full, base_path)
            result += "# [%s](%s)\n" % (md_content.title, path_to_file)

    return result


###############################################################################
# An object to set the menu List of Entry
###############################################################################
def preprocess_menu_dir(text, search_folder, base_path):
    # search begin
    match_file = re.search(__include_dir_re__, text, flags=re.MULTILINE)

    # finish if no match
    if not match_file:
        return text

    # There is a match
    folder = os.path.join(search_folder, match_file.group('name'))
    logging.debug('Find the folder to include %s', folder)

    # if base_path != search_folder:
    #     mv_base_path = os.path.relpath(search_folder, base_path)
    #     folder = os.path.join(mv_base_path, folder)

    text_file = create_menu_from_folder(folder, base_path)
    text_file = text_file.rstrip('\n\r ')

    text_file = re.sub("^", match_file.group('level')[:-1],
                       text_file, flags=re.MULTILINE)

    result = text[:match_file.start(0)]
    result += text_file + '\n'
    result += preprocess_menu(text[match_file.end(0):], base_path, base_path)

    return result

###############################################################################
# An object to set the menu List of Entry
###############################################################################
def preprocess_menu_include(text, search_folder, base_path):
    # search begin
    match_file = re.search(__include_menu_re__, text, flags=re.MULTILINE)

    # finish if no match
    if not match_file:
        return text

    # There is a match
    filename = os.path.join(search_folder, match_file.group('name'))
    logging.debug('Find the file %s', filename)

    text_file = common.get_file_content(filename)
    text_file = preprocess_menu(text_file,
                                os.path.split(filename)[0],
                                base_path)
    text_file = re.sub("^", match_file.group('level'),
                       text_file, flags=re.MULTILINE)

    result = text[:match_file.start(0)]
    result += text_file
    result += preprocess_menu(text[match_file.end(0):],
                              search_folder, base_path)

    return result

###############################################################################
# Add a label for link with empty label
###############################################################################
def preprocess_menu_add_label(text, base_path):
    links = mdcommon.search_link_in_md_text(text)
    replace_links = []
    for link in links:
        if (not mdcommon.is_external_link(link['url'])) and \
                (link['name'] is None or len(link['name']) == 0):
            new_link = copy.deepcopy(link)
            content = mdfile.MarkdownContent(os.path.join(base_path,
                                                          new_link['url']))

            new_link['name'] = content.title
            if 'title' in content:
                new_link['name'] = content['title']

            replace_links.append((link, new_link))

    return mdcommon.update_links_from_old_link(text, replace_links)

###############################################################################
# An object to set the menu List of Entry
###############################################################################
# @tools.handle_exception("Préparation du fichier menu",
#                         base_path="Répertoire racine",
#                         search_folder="Répertoire de recherche")
def preprocess_menu(text, search_folder, base_path):

    # change the start of the relative files
    search_folder = common.set_correct_path(search_folder)
    base_path = common.set_correct_path(base_path)
    if base_path != search_folder:
        mv_base_path = os.path.relpath(search_folder, base_path)
        text = mdcommon.move_base_path_in_md_text(text, mv_base_path)

    result = text
    result = preprocess_menu_include(result, search_folder, base_path)
    result = preprocess_menu_dir(result, search_folder, base_path)
    result = preprocess_menu_add_label(result, base_path)
    result = pymdtools.instruction.strip_xml_comment(result)

    return result


###############################################################################
# An object to set the menu List of Entry
###############################################################################
# @tools.handle_exception("Lecture du fichier menu",
#                         md_filename="Fichier menu",
#                         base_path="Répertoire racine")
def read_menu(md_filename, base_path):
    md_content = common.get_file_content(md_filename)
    # add includes
    md_content = preprocess_menu(text=md_content,
                                 search_folder=os.path.split(md_filename)[0],
                                 base_path=base_path)

    toc = md2py.md2py(md_content)

    def process_entry(node):
        result = Entry()

        label = markdownify.markdownify(str(node.source),
                                        convert=['a']).rstrip('\n')
        links = mdcommon.search_link_in_md_text(label)

        # if len(links) > 1:
        #     logging.error('Too many links in the entry %s of the file %s',
        #                   label, md_filename)
        #     raise RuntimeError('Too many links in the entry %s of the file %s'
        #                        % (label, md_filename))
        if len(links) == 1:
            the_link = links[0]
            result = Entry(**the_link)

        if len(links) == 0:
            result.name = label

        if len(node.branches) != 0:
            for sub_node in node.branches:
                result.children.append(process_entry(sub_node))

        return result

    return process_entry(toc).children


###############################################################################
# An object to set the menu List of Entry
###############################################################################
class Menu(list):
    def init(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)

    ###########################################################################
    # Access to members by identifier
    # @param the function to apply to all elements
    ###########################################################################
    def apply(self, fun):
        for entry in self:
            entry.apply(fun)

    ###########################################################################
    # Access to members by identifier
    # @return the list
    ###########################################################################
    def __getitem__(self, key):
        if isinstance(key, int):
            return list.__getitem__(self, key)

        for entry in self:
            if entry.name == key:
                return entry
        raise KeyError

    ###########################################################################
    # __str__ is a built-in function that computes the "informal"
    # string reputation of an object
    # __str__ goal is to be readable
    ###########################################################################
    def __str__(self):
        result = ""
        count = 0
        count_max = len(self)

        for entry in self:
            count += 1
            str_entry = re.sub("^", "       ",
                               str(entry), flags=re.MULTILINE).lstrip()

            result += "%02d/%02d: %s\n" % (count, count_max, str_entry)

        while len(result) > 0 and result[-1] == '\n':
            result = result[:-1]

        return result

###############################################################################
# An entry in the menu
###############################################################################
class Entry(mdcommon.Link):
    def __init__(self, **kwargs):
        mdcommon.Link.__init__(self, **kwargs)
        self.__children = Menu()

    ###########################################################################
    # Access to members by identifier
    # @param the function to apply to all elements
    ###########################################################################
    def apply(self, fun):
        fun(self)
        self.children.apply(fun)

    ###########################################################################
    # the children
    # @return the value
    ###########################################################################

    @property
    def children(self):
        return self.__children

    ###########################################################################
    # the children
    # @param value The value to set
    ###########################################################################
    @children.setter
    def children(self, value):
        self.__children = value

    ###########################################################################
    # __str__ is a built-in function that computes the "informal"
    # string reputation of an object
    # __str__ goal is to be readable
    ###########################################################################
    def __str__(self):
        result = "name=%s title=%s url=%s" % (self.name, self.title, self.url)

        str_children = str(self.children)
        if len(str_children) > 0:
            result += "\n" + str_children

        return result
