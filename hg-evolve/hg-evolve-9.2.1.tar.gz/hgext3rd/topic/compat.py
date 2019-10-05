# Copyright 2017 FUJIWARA Katsunori <foozy@lares.dti.ne.jp>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""
Compatibility module
"""
from __future__ import absolute_import

from mercurial import (
    obsolete,
    pycompat,
)

getmarkers = None
successorssets = None
try:
    from mercurial import obsutil
    getmarkers = getattr(obsutil, 'getmarkers', None)
    successorssets = getattr(obsutil, 'successorssets', None)
except ImportError:
    pass

if getmarkers is None:
    getmarkers = obsolete.getmarkers
if successorssets is None:
    successorssets = obsolete.successorssets

if pycompat.ispy3:
    def branchmapitems(branchmap):
        return branchmap.items()
else:
    # py3-transform: off
    def branchmapitems(branchmap):
        return branchmap.iteritems()
    # py3-transform: on
