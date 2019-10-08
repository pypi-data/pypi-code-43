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

Script to set the properties about a project.

"""
import logging
import sys

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient


class LbSdbSetPVProperties(LbSoftConfDbBaseClient):
    """ Update a property for a project:

    lb-sdb-setpvprops <project name> <version> <prop name> <value>

    To remove a specific property:

    lb-sdb-setpvprops -r <project name>  <version> <prop name>

    To remove all properties:

    lb-sdb-setpvprops -r <project name>  <version>

    """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(
            self, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("-r",
                          dest="reset",
                          action="store_true",
                          default=False,
                          help="Reset the properties")

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """

        opts = self.options
        args = self.args
        if opts.reset:
            if len(args) < 2:
                self.log.error("Not enough arguments: "
                               "please specify the project name version")
                sys.exit(1)
            else:
                project = args[0].upper()
                version = args[1]

                if len(args) == 2:
                    self.getRWInterface().resetPVProperties(project, version)
                    sys.exit(0)
                else:
                    propname = args[2]
                    self.getRWInterface().setPVProperty(
                        project, version, propname, None)
                    sys.exit(0)

        if len(args) < 4:
            self.log.error("Not enough arguments: please specify "
                           "<project name> <version> <prop name> <prop value>")
            sys.exit(1)
        else:
            project = args[0].upper()
            version = args[1]
            propname = args[2]
            propval = args[3]

        self.getRWInterface().setPVProperty(
            project, version, propname, propval)


def main():
    sUsage = """%prog project version propname propval
    Sets a property on a given project/version
    """
    s = LbSdbSetPVProperties(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
