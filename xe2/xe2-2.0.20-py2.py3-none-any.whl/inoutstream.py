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
# @package mdtools
# Markdown Tools develops for Gucihet Entreprises
#
###############################################################################

import sys

###############################################################################
# NullStream behaves like a stream but does nothing.
###############################################################################
class NullStream:
    def __init__(self):
        pass

    def write(self, data):
        pass

    def read(self, data):
        pass

    def flush(self):
        pass

    def close(self):
        pass


###############################################################################
# Storage for stream
###############################################################################
class InOutStream:
    def __init__(self, stream=NullStream()):
        self.stdout = stream
        self.stderr = stream
        self.stdin = stream
        self.__stdout__ = stream
        self.__stderr__ = stream
        self.__stdin__ = stream

    def save_current_stream(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.stdin = sys.stdin
        self.__stdout__ = sys.__stdout__
        self.__stderr__ = sys.__stderr__
        self.__stdin__ = sys.__stdin__

    def apply_to_std_stream(self):
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        sys.stdin = self.stdin
        sys.__stdout__ = self.__stdout__
        sys.__stderr__ = self.__stderr__
        sys.__stdin__ = self.__stdin__


###############################################################################
# define a static decorator for function
#
# @code{.py}
# 	(at)static(__folder_md_test__=None)
# 	def get_test_folder():
#     		if get_test_folder.__folder_md_test__ is None:
#         	get_test_folder.__folder_md_test__ = check_folder(os.path.join(
#             		os.path.split(__get_this_filename())[0], "test-md"))
#     		return get_test_folder.__folder_md_test__
# @endcode
#
# @param kwargs list of arguments
# @return the wrap function
###############################################################################
def static(**kwargs):
    def wrap(the_decorated_function):
        for key, value in kwargs.items():
            setattr(the_decorated_function, key, value)
        return the_decorated_function
    return wrap


###############################################################################
# Retrieve the initial stream
###############################################################################
@static(__stream__=None)
def initial_stream():
    if initial_stream.__stream__ is None:
        initial_stream.__stream__ = InOutStream()
        initial_stream.__stream__.save_current_stream()
    return initial_stream.__stream__


###############################################################################
# Test the frozen situation of the executable
###############################################################################
def is_frozen():
    return getattr(sys, 'frozen', False)


###############################################################################
# Change the std stream in the frozen case
###############################################################################
if is_frozen():
    initial_stream().save_current_stream()
    # InOutStream(NullStream()).apply_to_std_stream()
