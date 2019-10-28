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
# standard object to wrap file and access easily to the file resources
###############################################################################

import logging
import os
import os.path
import shutil

import pymdtools.common as common
import pymdtools.filetools as filetools


###############################################################################
# Object for a resource.
# Provide manipulation on filename
# Can be a object base for other purpose.
###############################################################################
class Resource(filetools.FileName):

    ###########################################################################
    # Initialize the object with the filename
    #
    # @param filename the filename to deal with
    ###########################################################################
    def __init__(self, filename, base_path):
        filetools.FileName.__init__(self, filename=filename)

        self.__base_path = None
        self.__relative_path = None

        self.__base_path = base_path
        self.compute_relative_path()

    ###########################################################################
    # the full filename with the complet path
    # @return the value
    ###########################################################################
    @property
    def base_path(self):
        return self.__base_path

    ###########################################################################
    # the full filename with the complet path
    # @param value The value to set
    ###########################################################################
    @base_path.setter
    def base_path(self, value):
        if value is None:
            logging.error('the new base path can not be None')
            raise Exception('the new base path can not be None')

        new_base_path = common.set_correct_path(value)

        if len(self.filename_path) < len(new_base_path) and \
                self.filename_path[0:len(new_base_path)] != new_base_path:
            logging.error('the new base path is not good')
            raise Exception('the new base path is not good')

        self.__base_path = new_base_path

    ###########################################################################
    # the full filename with the complet path
    # @return the value
    ###########################################################################
    @property
    def relative_path(self):
        return self.__relative_path

    ###########################################################################
    # the full filename with the complet path
    # @param value The value to set
    ###########################################################################
    @relative_path.setter
    def relative_path(self, value):
        if value is None:
            logging.error('the new relative path can not be None')
            raise Exception('the new relative path can not be None')

        new_relative_path = os.path.normcase(value.lower())
        new_relative_path = os.path.normpath(new_relative_path)

        self.__relative_path = new_relative_path

    ###########################################################################
    # the full filename with the complet path
    # @return the value
    ###########################################################################
    def target_filename(self, dest_root_path):
        output_folder = os.path.join(dest_root_path, self.relative_path)
        common.check_create_folder(output_folder)
        return os.path.join(output_folder, self.filename)

    ###########################################################################
    # test if the file exist
    # @return the result of the test
    ###########################################################################
    def compute_relative_path(self):
        result = os.path.relpath(self.filename_path, self.base_path)
        self.relative_path = result
        return result

    ###########################################################################
    # test if the file exist
    # @return the result of the test
    ###########################################################################
    @property
    def relative_filename(self):
        result = os.path.relpath(self.full_filename, self.base_path)
        return result

    ###########################################################################
    # test if the file exist
    # @return the result of the test
    ###########################################################################
    def copy(self, dest_root_path):
        result = self.target_filename(dest_root_path)
        shutil.copyfile(self.full_filename, result)
        return result

    ###########################################################################
    # __repr__ is a built-in function used to compute the "official"
    # string reputation of an object
    # __repr__ goal is to be unambiguous
    ###########################################################################
    def __repr__(self):
        return filetools.FileName.__repr__(self)

    ###########################################################################
    # __str__ is a built-in function that computes the "informal"
    # string reputation of an object
    # __str__ goal is to be readable
    ###########################################################################
    def __str__(self):
        result = filetools.FileName.__str__(self)
        result += "Base path=%s\n" % self.base_path
        result += "Relative path=%s\n" % self.relative_path
        result += "Relative filename=%s\n" % self.relative_filename

        return result

###############################################################################
# Object for a resource.
# Provide manipulation on filename
# Can be a object base for other purpose.
###############################################################################
class ResourceGroup:

    ###########################################################################
    # Initialize the object with the filename
    #
    # @param filename the filename to deal with
    ###########################################################################
    def __init__(self, base_path):
        self.__base_path = common.check_folder(base_path)
        self.__resources = {}

    ###########################################################################
    # Add files from the folder
    #
    # @param filter_for_files filter for files
    # @param folder the folder to find files
    ###########################################################################
    def add_files(self, filter_for_files=None, folder=None):
        if folder is None:
            folder = self.base_path

        def fun_filter(_unused):
            return True

        if filter_for_files is not None:
            fun_filter = filter_for_files

        for root, unused_dirs, files in os.walk(folder):
            for filename in files:
                complet_filename = os.path.join(root, filename)
                complet_filename = common.set_correct_path(complet_filename)
                if fun_filter(complet_filename):
                    self += Resource(complet_filename, self.base_path)

    ###########################################################################
    # Build a library of resources
    # @return the library
    ###########################################################################
    def build_lib(self, filename_ext):
        result = {}
        for key in self:
            if self[key].filename_ext in filename_ext:
                value = self[key].relative_filename.replace('\\', '/')
                result[self[key].filename] = value
        return result

    ###########################################################################
    # the members list
    # @return the list
    ###########################################################################
    @property
    def resources(self):
        return self.__resources

    ###########################################################################
    # the members list
    # @return the list
    ###########################################################################
    @property
    def base_path(self):
        return self.__base_path

    ###########################################################################
    # Access to members by identifier
    # @return the list
    ###########################################################################
    def __getitem__(self, key):
        return self.resources[key]

    ###########################################################################
    # Access to members by identifier
    # @return the list
    ###########################################################################
    def __delitem__(self, key):
        if key in self.__resources:
            del self.__resources[key]

    ###########################################################################
    # test if a member is in the list
    # @return result of the test
    ###########################################################################
    def __contains__(self, key):
        if isinstance(key, Resource):
            return key.relative_filename in self.__resources
        return key in self.__resources

    ###########################################################################
    # define iterator
    # @return the iterator
    ###########################################################################
    def __iter__(self):
        return self.__resources.__iter__()

    ###########################################################################
    # Access to members
    # @return the length of the list
    ###########################################################################
    def __len__(self):
        return len(self.resources)

    ###########################################################################
    # Access to members
    # @return the length of the list
    ###########################################################################
    def __iadd__(self, value):
        resource = value
        if isinstance(value, str):
            resource = Resource(value, self.base_path)

        self.__resources[resource.relative_filename] = resource
        return self

    ###########################################################################
    # Access to members
    # @return the length of the list
    ###########################################################################
    def __isub__(self, resource):
        self.__delitem__(resource.relative_filename)

    ###########################################################################
    # test if the file exist
    # @return the result of the test
    ###########################################################################
    def copy(self, dest_root_path):
        for key in self.resources:
            self[key].copy(dest_root_path)

    ###########################################################################
    # __repr__ is a built-in function used to compute the "official"
    # string reputation of an object
    # __repr__ goal is to be unambiguous
    ###########################################################################
    def __repr__(self):
        return repr(self.__resources)

    ###########################################################################
    # __str__ is a built-in function that computes the "informal"
    # string reputation of an object
    # __str__ goal is to be readable
    ###########################################################################
    def __str__(self):
        result = ""
        result += "Base path=%s\n" % self.base_path
        counter = 0
        max_counter = len(self)
        for key in self.resources:
            counter += 1
            result += "%03d / %03d --> %s:%s\n" % (
                counter, max_counter, key, self[key])

        return result
