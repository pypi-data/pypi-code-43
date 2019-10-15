# conduit.version
# Maintains version and package information for deployment.
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Apr 23 18:05:50 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: version.py [] benjamin@bengfort.com $

"""
Maintains version and package information for deployment.
"""

##########################################################################
## Module Info
##########################################################################

__version_info__ = {
    'major': 1,
    'minor': 1,
    'micro': 0,
    'releaselevel': 'final',
    'serial': 2,
}

##########################################################################
## Helper Functions
##########################################################################

def get_version(short=False):
    """
    Prints the version.
    """
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ["%(major)i.%(minor)i" % __version_info__, ]
    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('%s%i' % (__version_info__['releaselevel'][0],
                              __version_info__['serial']))
    return ''.join(vers)
