# conduit
# Python stream transformation package for common Power Engineering analytics.
#
# Author:   Benjamin Bengfort <benjamin@pingthings.io>
# Created:  Tue Apr 23 18:02:47 2019 -0400
#
# Copyright (C) 2019 PingThings, Inc. and Kevin D. Jones
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Python stream transformation package for common Power Engineering analytics.
"""

##########################################################################
## Package Version
##########################################################################

from .version import get_version, __version_info__
__version__ = get_version(short=True)


##########################################################################
## High-level package contents
##########################################################################

from .base import Conduit
from .phasor import Phasor, PhasorGroup, PhasorPair, PhasorPairGroup