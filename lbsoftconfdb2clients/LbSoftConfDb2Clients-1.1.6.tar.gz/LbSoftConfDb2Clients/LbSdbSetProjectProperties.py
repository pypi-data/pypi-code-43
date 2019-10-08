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


class LbSdbSetProjectProperties(LbSoftConfDbBaseClient):
    """ Update a property for a project:

    lb-sdb-setprojectprops <project name> <prop name> <value>

    To remove a specific property:

    lb-sdb-setprojectprops -r <project name> <prop name>

    To remove all properties:

    lb-sdb-setprojectprops -r <project name>

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
        name = None

        if opts.reset:
            if len(args) < 1:
                self.log.error(
                    "Not enough arguments: please specify the project name")
                sys.exit(1)
            else:
                project = args[0].upper()
                if len(args) == 1:
                    self.getRWInterface().resetProjectProperties(project)
                    sys.exit(0)
                else:
                    propname = args[1]
                    self.getRWInterface().setProjectProperty(
                        project, propname, name)
                    sys.exit(0)

        if len(args) < 3:
            self.log.error(
                "Not enough arguments: please specify "
                "<project name> <prop name> <prop value>")
            sys.exit(1)
        else:
            project = args[0].upper()
            propname = args[1]
            propval = args[2]

        # Connect to the ConfDB to update the platform
        self.getRWInterface().setProjectProperty(project, propname, propval)


def main():
    sUsage = """%prog project gitlabGroup gitlabName
    Sets a property on a given project
    """
    s = LbSdbSetProjectProperties(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
