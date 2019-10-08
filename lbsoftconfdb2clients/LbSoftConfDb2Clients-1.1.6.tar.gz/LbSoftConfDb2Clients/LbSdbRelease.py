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

Script to set the release request flag on a project/version

"""
import logging
import sys

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient


class LbSdbRelease(LbSoftConfDbBaseClient):
    """ Update information about a project / version """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(self, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("-r",
                          dest="remove",
                          action="store_true",
                          default=False,
                          help="Remove the link to the release node")

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """
        args = self.args
        if len(args) < 2:
            self.log.error("Not enough arguments")
            sys.exit(1)
        else:
            project = args[0].upper()
            version = args[1]

        # Connect to the ConfDB to update the platform
        if self.options.remove:
            self.getRWInterface().unsetReleaseFlag(project, version)
        else:
            self.getRWInterface().setReleaseFlag(project, version)


def main():
    sUsage = """%prog [-r] project
    Sets the project as an Application """
    s = LbSdbRelease(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
