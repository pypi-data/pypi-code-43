#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
***
Module: request_data - class to hold upstream request data
***
"""
# Copyright (C) Smart Arcs Ltd registered in the United Kingdom.
# Unauthorized copying of this file, via any medium is strictly prohibited
#
# This file is provided under a license as specified in the "LICENSE" file, which is part
# of this software package.
#
# Written by Smart Arcs <support@smartarchitects.co.uk>, August 2018

__author__ = "Smart Arcs"
__copyright__ = 'Smart Arcs Ltd'
__email__ = 'support@smartarchitects.co.uk'
__status__ = 'Development'


class RequestData(object):
    """
    Just a structure to hold parsed requests.
    """
    def __init__(self, reader_name, command_id, command_name, command_data=None, command_object=None, password=None):
        """

        :param reader_name: Name of the reader - this can be a technical name, or name of the user (from certificate)
        :type reader_name: str
        :param command_id: Client-chosen identification of the command to match requests and responses
        :type command_id: str
        :param command_name: Command name
        :type command_name: str
        :param command_data: Input data for the command
        :type command_data: str
        :param command_object It contains an optional identification of an entity to which the commad is linked
        :type command_object: str
        :param password will contain an optional password/PIN
        :type password: str
        """
        self.reader_name = reader_name
        self.command_id = command_id
        self.command_name = command_name
        self.password = password
        if command_data:
            self.command_data = "".join(command_data.split())  # remove all whitespaces
        else:
            self.command_data = None
        self.command_object = command_object
