#!/usr/bin/env python3
# coding=utf-8
# author: @netmanchris
# -*- coding: utf-8 -*-

import requests


def get_logs(hiome_core):
    '''
    Function to return logs from Hiome Core
    :param hiome_core:
    :return:
    '''
    path= 'http://{}/api/{}/logs'.format(hiome_core.ipaddress, hiome_core.api_version)
    return requests.get(path).json()

def get_rooms(hiome_core):
    '''
    Function to list rooms from Hiome Core
    :param hiome_core:
    :return:
    '''
    path = 'http://{}/api/{}/rooms'.format(hiome_core.ipaddress, hiome_core.api_version)
    return requests.get(path).json()


def get_sensors(hiome_core):
    '''
    Function to list sensors from Hiome Core
    :param hiome_core:
    :return:
    '''
    path = 'http://{}/api/{}/sensors'.format(hiome_core.ipaddress, hiome_core.api_version)
    return requests.get(path).json()