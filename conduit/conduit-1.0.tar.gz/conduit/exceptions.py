# conduit.exceptions
# Conduit exceptions, errors and warnings hierarchy
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Jun 25 14:35:09 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: exceptions.py [] benjamin@bengfort.com $

"""
Conduit exceptions, errors and warnings hierarchy
"""

##########################################################################
## Exceptions
##########################################################################

class ConduitException(Exception):
    """
    Top level exception for all conduit issues
    """
    pass


class ConduitTypeError(ConduitException, TypeError):
    """
    Bad type passed into a conduit function
    """
    pass


class ConduitValueError(ConduitException, ValueError):
    """
    Bad value passed into a conduit function
    """
    pass


class ValidationError(ConduitValueError):
    """
    The conduit composition is invalid
    """
    pass


##########################################################################
## Warnings
##########################################################################

class ConduitWarning(UserWarning):
    """
    A conduit specific warning to make it easier to filter
    """
    pass
