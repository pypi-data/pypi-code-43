###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Permission decorators for each SoftConfDb function. If a function is
accessible only in read mode, it should be decorated with @readOnly.
Otherwise, it should be decorated with @writeaAllowed. Non decorated functions
will not be exposed in the XMLRPC server.
"""


ACCESS_TYPE_READ_ONLY = 1
ACCESS_TYPE_WRITE_ALLOWED = 2
ACCESS_TYPE_NOT_EXPOSED = 3


def readOnly(func):
    """
    Decorator for read only functions
    :param func: the function to be decorated
    :return: the decorated function
    """
    func._access_type = ACCESS_TYPE_READ_ONLY
    return func


def writeAllowed(func):
    """
    Decorator for write allowed functions
    :param func: the function to be decorated
    :return: the decorated function
    """
    func._access_type = ACCESS_TYPE_WRITE_ALLOWED
    return func


def getAccessType(func):
    """
    Returns the permission type for a decorated function
    :param func: the decorated function
    :return: the access type of the function
    """
    try:
        return func._access_type
    except:
        return ACCESS_TYPE_NOT_EXPOSED
