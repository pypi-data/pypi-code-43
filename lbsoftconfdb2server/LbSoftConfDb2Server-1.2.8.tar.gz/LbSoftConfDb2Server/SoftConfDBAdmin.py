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
'''
Command line client for administration on SoftConfDB

:author: Chitic Stefan-Gabriel
'''
from __future__ import print_function
import logging
import argparse

try:
    from urlparse import urlsplit
except Exception as _:
    # Python 3 compatibility
    from urllib.parse import urlparse
import json

from LbSoftConfDb2Server.SoftConfDB import SoftConfDB
from LbSoftConfDb2Clients.AppImporter import GitlabProject


class SoftConfDbAdmin():

    def __init__(self):
        self.mDb = SoftConfDB()
        self.log = logging.getLogger(__name__)
        self.output = None

    def display(self):
        to_return = {}
        for project in self.mDb.listProjects():
            if not to_return.get(project):
                to_return[project] = {}
            for proj_version in self.mDb.listVersions(project):
                if proj_version[0] in ["LCG", "LCGCMT"]:
                    continue
                pv_node = self.mDb.getPV(proj_version[0], proj_version[1])
                if pv_node.sourceuri and \
                        urlsplit(pv_node.sourceuri).scheme == "svn":
                    continue
                gp = GitlabProject(proj_version[0], proj_version[1],
                                   self.mDb.getSourceURI(proj_version[0],
                                                         proj_version[1]))
                gp_commitID = gp.getCommitId()
                if gp_commitID is None:
                    continue

                different_commitId = gp_commitID != pv_node.commitID
                deps_not_match = False
                try:
                    gp_deps = gp.getDependencies()
                except:
                    continue
                deps = []
                for (dp, dv) in gp_deps:
                    deps.append(self.mDb.getPV(dp, dv))
                for dep in pv_node.requires:
                    if dep not in deps:
                        deps_not_match = True
                for dep in deps:
                    if dep not in pv_node.requires:
                        deps_not_match = True
                to_return[project][proj_version[1]] = {
                    'local_commitID': pv_node.commitID,
                    'git_commitID': gp_commitID,
                    'local_deps': [(n.project_name, n.version)
                                   for n in pv_node.requires
                                   if n is not None],
                    'git_deps': [(n.project_name, n.version)
                                 for n in deps if n is not None],
                    'is_different_commitID': different_commitId,
                    'deps_not_match': deps_not_match
                }
                print(proj_version[0], proj_version[1], pv_node.commitID,
                      gp_commitID, different_commitId, deps_not_match)

        if self.output:
            with open(self.output, 'w') as f:
                f.write(json.dumps(to_return))


def main():
    """Main function to lunch the script"""
    parser = argparse.ArgumentParser(
        description='CLI to perform admin operations and display info about'
                    ' SoftConfDB (e.g. diplay the sync between the DB and'
                    ' Gitlab, etc. ')
    admin = SoftConfDbAdmin()

    parser.add_argument('-d', '--debug',
                        dest="debug",
                        default=False,
                        action="store_true",
                        help="Show debug information")
    parser.add_argument('--info',
                        dest="info",
                        default=False,
                        action="store_true",
                        help="Show logging messages with level INFO")

    subparsers = parser.add_subparsers(
        title='subcommands', description='valid subcommands',
        help='')
    # Display
    subparsers_tmp = subparsers.add_parser(
        'display', help="Displays and performs sanity checks on the db "
                        "elements vs git info")
    subparsers_tmp.add_argument('--output',
                        dest="output",
                        default=None,
                        action="store",
                        help="Export data to output file as json payload")

    subparsers_tmp.set_defaults(which='display')

    args = vars(parser.parse_args())
    # Now setting the logging depending on debug mode...
    if args['debug'] or args['info']:
        logging.basicConfig(format="%(levelname)-8s: "
                                   "%(funcName)-25s - %(message)s")
        if args['info']:
            logging.getLogger().setLevel(logging.INFO)
        else:
            logging.getLogger().setLevel(logging.DEBUG)
    if args['output']:
        admin.output = args['output']
    mode = args['which']
    getattr(admin, mode)()


if __name__ == '__main__':
    main()
