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
A script to import a project into the Software Configuration DB

"""
import logging
import sys

from LbSoftConfDb2Clients.AppImporter import AppImporter

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient


class LbSdbImportProject(LbSoftConfDbBaseClient):
    """ Main scripts class for looking up dependencies.
    It inherits from """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(
            self, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("--norelease",
                          dest="norelease",
                          default=False,
                          action="store_true",
                          help="Disable automatic release of projects "
                               "not yet in DB")
        parser.add_option("--sourceuri",
                          dest="sourceuri",
                          default=None,
                          action="store",
                          help="Specify the location of the project")
        parser.add_option("--buildtool",
                          dest="buildtool",
                          default=None,
                          action="store",
                          type="choice",
                          choices=["cmt", "cmake"],
                          help="Specify the build tool to use")
        parser.add_option("--platforms",
                          dest="platforms",
                          default=None,
                          action="store",
                          help="Specify the platforms to release, "
                               "as a comma separated list")

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """
        opts = self.options
        args = self.args

        if len(args) < 2:
            self.log.error("Not enough arguments")
            sys.exit(1)
        else:
            project = args[0].upper()
            version = args[1]

            # Creating the object to import dependencies
            platform_list = []
            if opts.platforms:
                platform_list = [p.strip() for p in opts.platforms.split(",")]
            self.mAppImporter = AppImporter(self.getRWInterface(),
                                            self.getROInterface(),
                                            not opts.norelease, platform_list)

            self.log.info("Checking SoftConfDB for %s %s" % (project,
                                                             version))
            self.mAppImporter.processProjectVersion(
                project, version, sourceuri=opts.sourceuri)

            # Now setting the build tools as requested
            if opts.buildtool is not None:
                self.getRWInterface().setBuildTool(
                    project, version, opts.buildtool)


def main():
    sUsage = """%prog [-n] project version  """
    s = LbSdbImportProject(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
