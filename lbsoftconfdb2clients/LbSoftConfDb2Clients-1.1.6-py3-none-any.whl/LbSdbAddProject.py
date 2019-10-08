#!/usr/bin/env python
###############################################################################
# (c) Copyright 2018-2019 CERN                                                #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

"""
A script to add  a new  project to the SoftConfDB

"""
import sys

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient


class LbSdbAddProject(LbSoftConfDbBaseClient):
    """ Script to add a project to the Software Configuration DB.
    Use:
    LbSdbAddPlatform project version sourceuri
    Where the sourceuri is the source location e.g. gitlab-cern:lhcb/DaVinci
    """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(self, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        pass

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """
        args = self.args

        if len(args) < 2:
            self.log.error("Not enough arguments")
            sys.exit(1)
        else:
            project = args[0].upper()
            sourceuri = args[1]
            self.getRWInterface().createProjectSerializable(project,
                                                            sourceuri)


def main():
    sUsage = """%prog project sourceuri"""
    s = LbSdbAddProject(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
