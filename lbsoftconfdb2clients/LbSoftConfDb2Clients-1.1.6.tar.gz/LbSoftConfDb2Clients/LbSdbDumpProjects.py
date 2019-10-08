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

Script to dump the information known about project

"""
import logging
import json
import sys
from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient


class LbSdbDumpProjects(LbSoftConfDbBaseClient):
    """ Dump the information known about projects """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(
            self, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("-o",
                          dest="fileoutput",
                          action="store",
                          default=None,
                          help="Store result in file")

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """

        opts = self.options

        raw = self.getROInterface().dumpAllProjectProperties()
        props = {}
        for key in raw.keys():
            sourceuri = raw[key].get('sourceuri', None)
            props[key] = {
                'project': raw[key].get('name')
            }
            if sourceuri:
                props[key]['sourceuri'] = sourceuri

        fp = sys.stdout
        if opts.fileoutput is not None:
            fp = open(opts.fileoutput, "w")
        json.dump(props, fp)
        if opts.fileoutput is not None:
            fp.close()


def main():
    sUsage = """%prog [-r] project
    Sets the project as an Application """
    s = LbSdbDumpProjects(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
