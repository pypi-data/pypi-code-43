#!/usr/bin/env python
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

Script to generate the JSON file with the list of versions

"""
import logging
import sys
from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient


class LbSdbGenerateVersionJSON(LbSoftConfDbBaseClient):
    """ Update information about a project / version to say
    whether it was built with CMake or CMT"""

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(
            self, *args, **kwargs)

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """
        known_tags = ["prod"]

        allvers = {}
        for tag in known_tags:
            tmplist = []
            for p in sorted(self.getROInterface().listTag(tag.upper())):
                tmplist.append(p)
            allvers[tag] = tmplist

        import json
        print(json.dumps(allvers, indent=2))


def main():
    sUsage = """%prog [-r] project version tag
    Sets the flag indicating which buildtool is used for the build"""
    s = LbSdbGenerateVersionJSON(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
