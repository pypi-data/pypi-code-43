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
Created on May 6, 2013

@author: Ben Couturier
"""
import inspect
import logging
import sys

from LbSoftConfDb2Clients.GenericClient import LbSoftConfDbBaseClient
from LbSoftConfDb2Clients.SoftConfDB import sortVersions
from LbEnv import fixProjectCase


class LbSdbQuery(LbSoftConfDbBaseClient):
    """ Main scripts class for looking up dependencies.
    It inherits from """

    def __init__(self, *args, **kwargs):
        LbSoftConfDbBaseClient.__init__(self, *args, **kwargs)

    def defineOpts(self):
        """ Script specific options """
        parser = self.parser
        parser.add_option("--json",
                          dest="json",
                          default=False,
                          action="store_true",
                          help="JSON output format")
        parser.add_option("--debug-py2neo",
                          dest="debugpy2neo",
                          default=False,
                          action="store_true",
                          help="Set the logvel to debug for py2neo")

    def main(self):
        """ Main method for bootstrap and parsing the options.
        It invokes the appropriate method and  """
        opts = self.options
        args = self.args

        if len(args) == 0:
            self.log.error("Please specify a command name")
            self.parser.print_help()
            sys.exit(1)

        # Initializing the ConfDB interface
        if opts.log_level == 'DEBUG':
            self.getROInterface().log.setLevel(logging.DEBUG)
        else:
            self.getROInterface().log.setLevel(logging.WARNING)

        # Locating the command...
        cmdShort = {'l': 'listProjects', 'i': 'listApplications',
                    'v': 'listVersions', 'p': 'listPlatforms',
                    'd': 'listDependencies', 'r': 'listReferences',
                    'u': 'listUsed', 'a': 'listActive',
                    's': 'listActiveReferences'
                    }
        command = args[0]
        if command in list(cmdShort.keys()):
            command = cmdShort[command]
        method = self._findMethod(self, "cmd", command)

        if method is None:
            raise Exception("Could not find command '%s'."
                            " See --help for a list of commands" % command)

        # And invoking it...
        tmpargs = args[1:]
        # Setting to verbose mode
        if command.lower() == 'checkunused' and opts.verbose is not None:
            tmpargs.append(opts.verbose)
        method(tmpargs)

    # Know commands forwarded to the DB
    ###########################################################################
    def cmdProjectExists(self, args):
        """ List the projects known by the SoftConfDB """
        p = self.getROInterface().findVersion(args[0].upper(), args[1])
        return len(p) > 0

    def cmdlistProjects(self, args):
        """ List the projects known by the SoftConfDB """
        for p in sorted(self.getROInterface().listProjects()):
            print(p)

    def cmdlistDatapkgs(self, args):
        """ List the projects known by the SoftConfDB """
        for p in sorted(self.getROInterface().listDatapkgs()):
            print(p)

    def cmdlistApplications(self, args):
        """ List the projects known by the SoftConfDB """
        for p in sorted(self.getROInterface().listApplications()):
            print(p)

    def cmdlistReleases(self, args):
        """ List the projects known by the SoftConfDB """
        for p in sorted(self.getROInterface().listReleaseReqs()):
            print("%s\t%s" % tuple(p))

    def cmdlistCMake(self, args):
        """ List the projects built with CMake """
        for p in sorted(self.getROInterface().listCMakeBuiltProjects()):
            print("%s\t%s" % tuple(p))

    def cmdlistTag(self, args):
        """ List the projects with a given tag """
        if self.options.json:
            import json
            print(json.dumps(sorted(self.getROInterface().listTag(args[0].upper())),
                             indent=2))
        else:
            for p in sorted(self.getROInterface().listTag(args[0].upper())):
                print("%s\t%s\t%s" % tuple(p))

    def cmdlistCMT(self, args):
        """ List the projects built with CMT """
        for p in sorted(self.getROInterface().listCMTBuiltProjects()):
            print("%s\t%s" % tuple(p))

    def cmdGetBuildTool(self, args):
        """ List the projects built with CMT """

        if len(args) < 2:
            self.log.error("Please specify a project and version")
            sys.exit(1)

        pname = args[0].upper()
        pversion = args[1]
        if not self.cmdProjectExists(args):
            self.log.error("Could not find %s %s" % (pname, pversion))
            sys.exit(1)

        for p in self.getROInterface().getBuildTools(pname, pversion):
            print("%s" % p)

    def _sanitizeProjectName(self, pname):
        """ Puts back the correct case in display """
        return fixProjectCase(pname)

    def cmdlistReleaseStacks(self, args):
        """ List the projects known by the SoftConfDB """
        stacks = self.getROInterface().listReleaseStacks()
        stackdicts = []
        for stack in stacks:
            stackdict = {}

            stackdict["projects"] = [(self._sanitizeProjectName(p2), v2)
                                     for (p2, v2) in stack["path"]]

            stackdict["platforms"] = stack["platforms"]
            stackdict["build_tool"] = stack["build_tool"]
            psources = dict()
            for (p2, v2) in stack['path']:
                sp2 = self._sanitizeProjectName(p2)
                psources[sp2] = self.getROInterface().getSourceURI(p2, v2)
            stackdict["projects_sources"] = psources
            stackdicts.append(stackdict)

        if self.options.json:
            import json
            print(json.dumps(stackdicts, indent=2))
        else:
            for (i, sd) in enumerate(stackdicts):
                tmp = ">>>>>>>>> Stack %d " % i
                if "build_tool" in sd:
                    tmp += " build_tool: %s " % sd["build_tool"]
                print("%s Platforms: %s" % (tmp, ",".join(sd["platforms"])))
                for (p, v) in sd["projects"]:
                    sdict = sd.get("projects_sources", None)
                    sourceuri = ""
                    if sdict is not None:
                        sourceuri = sdict.get(p, "")
                    print("%d\t%s\t%s\t%s" % (i, p, v, sourceuri))

    def cmdlistActive(self, args):
        """ List active projects """
        for p in sorted(self.getROInterface().listActive()):
            print("%s %s" % (p[0], p[1]))

    def cmdlistActiveApplications(self, args):
        """ List active applications """
        for p in sorted(self.getROInterface().listActiveApplications()):
            print("%s %s" % (p[0], p[1]))

    def cmdlistUsed(self, args):
        """ List used projects """
        for p in sorted(self.getROInterface().listUsed()):
            print("%s %s" % (p[0], p[1]))

    def cmdCheckUnused(self, args):
        """ List used projects """
        for p in sorted(self.getROInterface().checkUnused(args[0])):
            print("%s %s" % tuple(p))

    def cmdlistVersions(self, args):
        """ List the number of versions known for a given project """

        if len(args) < 1:
            self.log.error("Please specify a project name")
            sys.exit(1)

        allvs = self.getROInterface().listVersions(args[0].upper())
        if len(allvs) > 0:
            proj = allvs[0][0]
            if allvs[0][1].startswith("v"):
                # Checking if we have LHCb Ordering
                vs = sortVersions([t[1] for t in allvs])
            else:
                # Or the normal sorting order
                vs = sorted([t[1] for t in allvs])

            # Now print out the results
            for v in vs:
                print("%s %s" % (proj, v))

    def cmdgetProperties(self, args):
        """ Gets the properties of a project  """

        if len(args) < 1:
            self.log.error("Please specify a project name")
            sys.exit(1)

        pname = args[0].upper()
        props = self.getROInterface().getProjectProperties(pname)
        import json
        print(json.dumps(props, indent=2))

    def cmdgetPVProperties(self, args):
        """ Gets the properties of a project  """

        if len(args) < 2:
            self.log.error("Please specify a project name and version")
            sys.exit(1)

        pname = args[0].upper()
        pver = args[1]
        props = self.getROInterface().getPVProperties(pname, pver)
        import json
        print(json.dumps(props, indent=2))

    def cmdlistDatapkgVersions(self, args):
        """ List the number of versions known for a given data package """

        if len(args) < 1:
            self.log.error("Please specify a data package name")
            sys.exit(1)

        allvs = self.getROInterface().listDatapkgVersions(args[0].upper())
        if len(allvs) > 0:
            proj = allvs[0][0]
            if allvs[0][1].startswith("v"):
                # Checking if we have LHCb Ordering
                vs = sortVersions([t[1] for t in allvs])
            else:
                # Or the normal sorting order
                vs = sorted([t[1] for t in allvs])

            # Now print out the results
            for v in vs:
                print("%s %s" % (proj, v))

    def cmdShow(self, args):
        """ Check the various atributes of a specific node """
        if len(args) < 2:
            self.log.error("Please specify a project and version")
            sys.exit(1)

        pname = args[0].upper()
        pversion = args[1]

        if not self.cmdProjectExists(args):
            self.log.error("Could not find %s %s" % (pname, pversion))
            sys.exit(1)

        print(self.getROInterface().show(pname, pversion))

    def cmdShowProject(self, args):
        """ Check the various atributes of a specific node """
        if len(args) < 1:
            self.log.error("Please specify a project")
            sys.exit(1)

        pname = args[0].upper()
        print((self.getROInterface().showProject(pname)))

    def cmdlistPlatforms(self, args):
        """ List the Platforms released for a Couple project version """
        if len(args) < 2:
            self.log.error("Please specify a project and version")
            sys.exit(1)

        pname = args[0].upper()
        pversion = args[1]
        if not self.cmdProjectExists(args):
            self.log.error("Could not find %s %s" % (pname, pversion))
            sys.exit(1)

        for p in sorted(self.getROInterface().listPlatforms(pname, pversion)):
            print(p)

    def cmdlistRequestedPlatforms(self, args):
        """ List the Platforms released for a Couple project version """
        if len(args) < 2:
            self.log.error("Please specify a project and version")
            sys.exit(1)

        pname = args[0].upper()
        pversion = args[1]
        if not self.cmdProjectExists(args):
            self.log.error("Could not find %s %s" % (pname, pversion))
            sys.exit(1)

        for p in sorted(self.getROInterface().listPlatforms(pname, pversion,
                                                   "REQUESTED_PLATFORM")):
            print(p)

    def cmdlistDependencies(self, args):
        """ List the project/versions the specified project depends on """
        if len(args) < 2:
            self.log.error("Please specify a project and version")
            sys.exit(1)

        pname = args[0].upper()
        pversion = args[1]
        if not self.cmdProjectExists(args):
            self.log.error("Could not find %s %s" % (pname, pversion))
            sys.exit(1)

        for p in self.getROInterface().listDependencies(pname, pversion):
            print("%s\t%s" % tuple(p))

    def cmdlistDependenciesAsDot(self, args):
        """ List the project/versions the specified project depends on """

        if len(args) % 2 != 0:
            self.log.error("Please specify project and version "
                           "for all projects")
            sys.exit(1)

        found = []
        not_found = []
        for (pname, pversion) in (args[pos:pos + 2]
                                  for pos in range(0, len(args), 2)):
            pkey = (pname.upper(), pversion)
            if not self.cmdProjectExists(pkey):
                not_found.append(pkey)
            else:
                found.append(pkey)

            if len(not_found):
                print("Not found: %s" %
                      ",".join(["%s_%s" % k for k in not_found]))

        print(self.getROInterface().getDependenciesAsDot(found))

    def cmddisplayDependenciesAsDot(self, args):
        """ List the project/versions the specified project depends on """

        if len(args) % 2 != 0:
            self.log.error("Please specify project and version for "
                           "all projects")
            sys.exit(1)

        found = []
        not_found = []
        for (pname, pversion) in (args[pos:pos + 2]
                                  for pos in range(0, len(args), 2)):
            pkey = (pname.upper(), pversion)
            if not self.cmdProjectExists(pkey):
                not_found.append(pkey)
            else:
                found.append(pkey)

        if len(not_found):
            print("Not found: %s" % ",".join(["%s_%s" % k for k in not_found]))

        dotfile = self.getROInterface().getDependenciesAsDot(found)

        from subprocess import Popen, PIPE
        dot = Popen('dot -Tsvg | display svg:-', stdin=PIPE, shell=True)
        dot.communicate(input=dotfile)
        dot.wait()

    def cmdlistReferencesAsDot(self, args):
        """ List the project/versions the specified project depends on """

        if len(args) % 2 != 0:
            self.log.error("Please specify project and "
                           "version for all projects")
            sys.exit(1)

        found = []
        not_found = []
        for (pname, pversion) in (args[pos:pos + 2]
                                  for pos in range(0, len(args), 2)):
            pkey = (pname.upper(), pversion)
            if not self.cmdProjectExists(pkey):
                not_found.append(pkey)
            else:
                found.append(pkey)

            if len(not_found):
                print("Not found: %s" %
                      ",".join(["%s_%s" % k for k in not_found]))

        print(self.getROInterface().getReferencesAsDot(found))

    def cmddisplayreferencesAsDot(self, args):
        """ List the project/versions the specified project depends on """

        if len(args) % 2 != 0:
            self.log.error("Please specify project and v"
                           "ersion for all projects")
            sys.exit(1)

        found = []
        not_found = []
        for (pname, pversion) in (args[pos:pos + 2]
                                  for pos in range(0, len(args), 2)):
            pkey = (pname.upper(), pversion)
            if not self.cmdProjectExists(pkey):
                not_found.append(pkey)
            else:
                found.append(pkey)

        if len(not_found):
            print("Not found: %s" %
                  ",".join(["%s_%s" % k for k in not_found]))

        dotfile = self.getROInterface().getReferencesAsDot(found)

        from subprocess import Popen, PIPE
        dot = Popen('dot -Tsvg | display svg:-', stdin=PIPE, shell=True)
        dot.communicate(input=dotfile)
        dot.wait()

    def cmdlistReferences(self, args):
        """ List the project/versions that depend on this project """

        if len(args) < 2:
            self.log.error("Please specify a project and version")
            sys.exit(1)

        pname = args[0].upper()
        pversion = args[1]
        if not self.cmdProjectExists(args):
            self.log.error("Could not find %s %s" % (pname, pversion))
            sys.exit(1)

        for p in self.getROInterface().listReferences(pname, pversion):
            print("%s\t%s" % tuple(p))

    def cmdlistActiveReferences(self, args):
        """ List the project/versions that depend on this project """

        if len(args) < 2:
            self.log.error("Please specify a project and version")
            sys.exit(1)

        pname = args[0].upper()
        pversion = args[1]
        if not self.cmdProjectExists(args):
            self.log.error("Could not find %s %s" % (pname, pversion))
            sys.exit(1)

        for p in self.getROInterface().listActiveReferences(pname, pversion):
            print("%s\t%s" % tuple(p))

    # Method that looks for a method name in the object passed
    # and returns it in order to set the attribute
    def _findMethod(self, obj, prefix, partialMethodName):
        """ Find the method named prefix +
        partialMethodName in the object instance """
        allmethods = inspect.getmembers(obj, predicate=inspect.ismethod)
        foundMethod = None
        for m in allmethods:
                if m[0].lower() == (prefix + partialMethodName.lower()):
                    self.log.debug("## Found Method " + m[0])
                    foundMethod = m[1]
        return foundMethod


def main():
    sUsage = \
    """%prog Command to query the Software Configuration database, which can be invoked in the following way: 

  %prog listProjects[l]                                    : List known projects
  %prog listVersions[v] <project>                          : List known version of a given project
  %prog listPlatforms[p] <project> <version>               : List the platforms this project id known to be released for
  %prog listRequestedPlatforms[p] <project> <version>               : List the platforms this project id known to be released for
  %prog listDependencies[d] <project> <version>            : List dependencies of a project/version
  %prog listDependenciesAsDot <p> <v> [<p> <v> ...]        : List dependencies of a project/version as a dot file
  %prog displayDependenciesAsDot <p> <v> [<p> <v> ...]     : display dependencies of a project/version as a dot file
                                                             (needs dot and display executables in the path)
  %prog listReferences[r] <project> <version>              : List project/versions using this one
  %prog listReferencesAsDot <p> <v> [<p> <v> ...]          : List project/versions using this one as a dot file
  %prog displayReferencesAsDot <p> <v> [<p> <v> ...]       : display project/versions of a project/version as a dot file
  %prog show <project> <version>                           : Show all properties and relationships of a project/version node
  %prog listReleases                                       : List projects flagged to be RELEASED
  %prog listReleaseStacks                                  : List projects flagged to be RELEASED grouping by stack with platforms
  %prog getBuildTool                                       : Get the build tool to use for this project
  %prog listDatapkgs                                       : List known Data packages
  %prog listDatapkgVersions <datapkg>                      : List known versions for the specified Data package
  %prog listTag <tag>                                      : List projects/version tagged with that specific value
  %prog getProperties <project>                            : Lists the properties of a project
  %prog getPVProperties <project> <version>                : Lists the properties of a project/version
    """  # nopep8
    s = LbSdbQuery(usage=sUsage)
    sys.exit(s.run())


if __name__ == '__main__':
    main()
