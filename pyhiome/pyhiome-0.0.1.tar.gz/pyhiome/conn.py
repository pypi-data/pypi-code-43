#!/usr/bin/env python3
# coding=utf-8
# author: @netmanchris
# -*- coding: utf-8 -*-

"""
This module contains functions for authenticating to the Attelani Brid Air Purifier Device
API.

"""


class HiomeCore:
    """
    Object to hold the authentication data for the Hiome API
    Note currently, the Hiome API requires no authentication. Auth object is created
    to allow for caching of IP address of Hiome Device and for future enhancements.
    :return An object of class HimoeCore to be passed into other functions to
    pass the authentication credentials
    """

    def __init__(self, ipaddress, api='1'):
        """
        This class acts as the auth object for the Hiome API.
        :param ipaddress: str object which contains the IP address or DNS name of the target Hiome Core Device
        """

        self.ipaddress = ipaddress
        self.api_version = api
        self.headers = {
            'Accept': 'application/json', 'Content-Type':
                'application/json', 'Accept-encoding': 'application/json'}