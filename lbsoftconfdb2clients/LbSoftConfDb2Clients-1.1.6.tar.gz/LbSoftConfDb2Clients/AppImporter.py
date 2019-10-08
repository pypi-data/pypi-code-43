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
A script to add a project to the Software Configuration DB

"""
import logging
import subprocess
import re

try:
    import urllib2
except Exception as _:
    import urllib.request as urllib2
import json

from LbCommon.CMake import getHeptoolsVersion, getGaudiUse
from LbEnv import fixProjectCase


def importerTranslateProject(p, v):
    """
    Function needed to prevent LCGCMT to be passed to translateProject
    as that does not work
    :param p: the project name
    :param v: the version name
    :return: the fixcase for the project and the version
    """
    if p.lower() == "lcgcmt" or p.lower() == "lcg":
        return (p.upper(), v)
    else:
        return (fixProjectCase(p), v)


class GitlabProject:
    """ Helper class to manager projects hosted in gitlab """

    def __init__(self, project, version, sourceuri):
        """
        :param project: project name in the git repository
        :param version: the version in the git repository
        :param sourceuri: the source uri for the project version in git repo
        """

        # SourceURI like: gitlab-cern:LHCb-SVN-mirrors/Brunel#v50r1

        self.log = logging.getLogger()
        self.project = project.upper()
        self.version = version

        # Hack alert: This should NOT be here, we need to find a
        # correct location
        # for all the  location for the constants for CERN gitlab...
        self.gitlabHTTPSURL = "https://gitlab.cern.ch"
        self.gitlabSSHURL = "ssh://git@gitlab.cern.ch:7999"
        self.gitlabViewURL = "https://gitlab.cern.ch"
        try:
            from urlparse import urlsplit
        except Exception as _:
            # Python 3 compatibility
            from urllib.parse import urlparse
        self.sourceuri = sourceuri
        url = urlsplit(sourceuri)
        self.scheme = url.scheme
        self.path = url.path

        tmp = self.path.split("/")
        if len(tmp) == 2:
            self.gitlabGroup = tmp[0]
            self.gitlabName = tmp[1]
        elif len(tmp) == 1:
            self.log.info("Path without Group/Name: %s, "
                          "using lhcb group by default" % self.path)
            self.gitlabGroup = "lhcb"
            self.gitlabName = tmp[0]

    def getCommitId(self):
        """ Returns the git commit ID for a specific project/version"""
        prefix = "%s/%s/%s/" % (self.gitlabViewURL,
                                self.gitlabGroup,
                                self.gitlabName)
        public_check_url = '%s/info/refs?service=git-upload-pack' % prefix
        try:
            urllib2.urlopen(public_check_url)
        except Exception as _:
            return None
        commitID = None
        commnad = ['git', 'ls-remote', prefix, self.version]
        cmd = subprocess.Popen(commnad, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = cmd.communicate()
        retCode = cmd.returncode
        if retCode != 0:
            self.log.error("Get commit id failed with: %s" % err)
        else:
            try:
                commitID = out.split()[0].strip()
            except Exception as _:
                self.log.error("CommitID parse failed for %s" % out)
        return commitID


    def getURL(self, file=None):
        """ Returns the URL at which files can be found in gitlab
        e.g. https://gitlab.cern.ch/gaudi/Gaudi/raw/v27r0/CMakeLists.txt
        :param file: file requested
        :return: the URL at which files can be found in gitlab
        """
        prefix = "%s/%s/%s/raw/%s" % (self.gitlabViewURL,
                                      self.gitlabGroup,
                                      self.gitlabName,
                                      self.version)
        if file is not None:
            return prefix + "/" + file
        else:
            return prefix

    def getToolchain(self):
        """
        Function used to get the tool chain
        :return: the tool chain found on gitlab if found
        """
        self.toolchainurl = self.getURL("toolchain.cmake")
        self.log.info("Reading toolchain.cmake from: %s" %
                      self.toolchainurl)
        response = urllib2.urlopen(self.toolchainurl)
        data = response.read()
        self.log.debug("Got: %s" % self.toolchainurl)
        return data

    def getCMakeLists(self):
        """
        Function used to get the cmake lists
        :return: the cmake lists on gitlab if found
        """
        self.cmakelistsurl = self.getURL("CMakeLists.txt")
        self.log.debug("Getting: %s" % self.cmakelistsurl)
        try:
            response = urllib2.urlopen(self.cmakelistsurl)
            data = response.read()
            self.log.debug("Got: %s" % self.cmakelistsurl)
        except Exception as _:
            self.log.info("Could not find CMakeLists at: %s" %
                          self.cmakelistsurl)
            raise
        return data

    def getProjectCMT(self):
        """
        Function used to get the CMT config file
        :return: the CMT config file on gitlab if found
        """
        self.projectcmturl = self.getURL("cmt/project.cmt")
        self.log.debug("Getting: %s" % self.projectcmturl)
        try:
            response = urllib2.urlopen(self.projectcmturl)
            data = response.read()
            self.log.debug("Got: %s" % self.projectcmturl)
        except Exception as _:
            self.log.info("Could not find Project.cmt at: %s" %
                          self.projectcmturl)
            raise
        return data

    def getProjectConfig(self):
        """ URL folows pattern:
        https://gitlab.cern.ch/lhcb-dirac/LHCbDIRAC/
        raw/v8r6p3/dist-tools/projectConfig.json
        :return: the project config on git if found
        """
        self.projconfigurl = self.getURL("dist-tools/projectConfig.json")
        self.log.debug("Getting: %s" % self.projconfigurl)
        try:
            response = urllib2.urlopen(self.projconfigurl)
            data = response.read()
            self.log.debug("Got: %s" % self.projconfigurl)
        except Exception as e:
            self.log.info("Could not find projectConfig.json at: %s" %
                          self.projconfigurl)
            raise e
        return data

    def getDepsFromProjectConfig(self, data):
        """
        Gets the project dependencies form the config file
        :param data: the row data with the projects used
        :return: a list of tuples (project, version) for dependencies
        """
        pc = json.loads(data)
        used_projects = pc["used_projects"]
        deps = []
        for l in used_projects["project"]:
            deps.append((l[0], l[1]))
        return deps

    def getDepsFromProjectCMT(self, data):
        """
        Gets the project dependencies form the CMT config file
        :param data: the row data with the projects used
        :return: a list of tuples (project, version) for dependencies
        """
        deps = []
        for l in data.splitlines():
            m = re.match("\s*use\s+(\w+)\s+([\w\*]+)", l)  # nopep8
            if m is not None:
                dp = m.group(1)
                dv = m.group(2)
                # removing the project name from the version if there
                dv = dv.replace(dp + "_", "")
                deps.append((dp, dv))
        return deps

    def getDependencies(self):
        """ Returns the list of project dependencies
        :return: a list of tuples (project, version) for dependencies
        """
        pupper = self.project.upper()
        if pupper in ["GAUDI", "GEANT4"]:
            # For GAUDI we take the dependency in the toolchain file
            try:
                data = self.getToolchain()
                htv = getHeptoolsVersion(data)
                deplist = [("LCG", htv)]
                return deplist
            except Exception as _:
                # In this case Gaudi is probably still using CMT
                self.log.info("Looking for legacy CMT project.cmt")
                data = self.getProjectCMT()
                deplist = self.getDepsFromProjectCMT(data)
                return deplist

        if pupper in ["DIRAC", "LHCBGRID"]:
            return []
        else:
            # For all other projects use the gaudi_project macro
            # First we try to find teh CMakeLists
            # Second we try the projectConfig.json
            # Third we try the project.cmt for legacy projects
            try:
                self.log.info("Looking for CMakeLists.txt")
                data = self.getCMakeLists()
                deplist = getGaudiUse(data)
                return deplist
            except Exception as _:
                try:
                    self.log.info("Looking for projectConfig.json")
                    data = self.getProjectConfig()
                    deplist = self.getDepsFromProjectConfig(data)
                    return deplist
                except Exception as _:
                    try:
                        self.log.info("Looking for legacy CMT project.cmt")
                        data = self.getProjectCMT()
                        deplist = self.getDepsFromProjectCMT(data)
                        return deplist
                    except Exception as _:
                        self.log.error(
                            "Could not find project dependency metadata")
                        raise Exception("Could not find project metadata")


class AppImporter:
    """ Tool to add new project/version to the Software configuration
    DB from the version control systems """

    def __init__(self, confDb, confDbReadOnly, autorelease=True,
                 platforms=None):
        """
        :param confDb: Instance for SoftConfDB (XMLRPC mode or local) in
                       write mode
        :param confDbReadOnly: Instance for SoftConfDB (XMLRPC mode or local)
                               in read only mode
        :param autorelease: flag to mark the autorelease fo the imported
                            projects
        :param platforms: a list of platforms used for this import
        """
        self.mConfDB = confDb
        self.mConfDBReadOnly = confDbReadOnly
        self.log = logging.getLogger()
        self.installArea = None
        self.mAutorelease = autorelease
        self.mPlatforms = platforms
        self.graph = []
        if self.mPlatforms is not None and len(self.mPlatforms):
            known_platforms = set(self.mConfDBReadOnly.listAllPlatforms())
            unknown = set(self.mPlatforms) - known_platforms
            for element in  unknown:
                self.log.info(
                    "Platform %s is not in the database. "
                    "It will be created!" % element)

    def _setRequestedPlatforms(self, project, version):
        """
        Sets the lists of platofrms as requested platforms for the project
        version pair
        :param project: the projects name
        :param version: the version of the projext
        """
        if self.mPlatforms:
            for p in self.mPlatforms:
                self.mConfDB.addPVPlatform(project, version, p,
                                           "REQUESTED_PLATFORM")

    def inGitlab(self, project, alturi=None):
        """ Check whether the project is handled in GIT or SVN

        :param project: the project name
        :param alturi: alternative uri for the source uri
        :return: True if the project is in Git repo, False otherwise
        """
        if not project:
            raise Exception("inGitlab method called with None project")

        if project.upper() in ["LCG", "LCGCMT"]:
            return False

        sourceuri = None
        if alturi is None:
            props = self.mConfDBReadOnly.getProjectProperties(project.upper())
            if props is not None and "sourceuri" in props.keys():
                sourceuri = props["sourceuri"]
        else:
            sourceuri = alturi

        from urlparse import urlsplit
        if sourceuri is not None:
            if urlsplit(sourceuri).scheme == "svn":
                return False

        return True

    def gitlabProcessProjectVersion(self, p, v,
                                    alturi=None, saveURIinPV=False,
                                    graph=[]):
        """ Processes the import of a project version that is found in GIT repo
        It starts with the top project imported and recursively builds a local
        representations of the dependencies graph that needs to be imported
        If the pair project version is the top element of the local graph, it
        sends a bulk update command to SoftConfDB instance

        :param p: the project name
        :param v: the version of the project
        :param alturi: the alternative URI for the source URI
        :param saveURIinPV: flag used to notify SoftConfDB instance to persist
                            the sourceURI in the database
        :param graph: local representations of the dependecies graph of the all
                      imported projects
        :return: the top project imported node instance
        """
        # Cleanup the project name and version

        (proj, ver) = (fixProjectCase(p), v)

        # Getting the project properties and locating the CMakeLists
        gp = GitlabProject(proj, ver, alturi)
        commitID = gp.getCommitId()
        deps = gp.getDependencies()

        # Formatting the project name/version
        corver = ver
        if proj in ver:
            corver = ver.replace(proj + "_", "")
        proj = proj.upper()

        # Looking for the project version in the DB
        tmp = self.mConfDBReadOnly.findVersion(proj, ver)
        createNode = False
        node_parent = None

        # First checking if the node is there with the correct revision
        if len(tmp) != 0:
            node = tmp[0]
            node_parent = node
            # Need to add commit to the DB
        # If the node does not exist just create it...
        else:
            createNode = True

        if createNode:
            self.log.info("Will create project %s %s" % (proj, ver))
            if saveURIinPV:
                self.log.info("Will set sourceuri=%s for %s %s" % (
                    gp.sourceuri, proj, ver))
            # If releasing is needed!
            if self.mAutorelease and proj.upper() not in ["LCG", "LCGCMT"]:
                self.log.info("Will request release of %s %s" % (proj,
                                                                 corver))
        graph_el = {
            'project': proj,
            'version': corver,
            'saveURIinPV': saveURIinPV,
            'createNode': createNode,
            'autorelease': self.mAutorelease,
            'mPlatforms': self.mPlatforms,
            'sourceuri': gp.sourceuri,
            'deps': [],
            'commitID': commitID
        }
        for (dp, dv) in deps:
            if dp in dv:
                dv = dv.replace(dp + "_", "")
            dp = dp.upper()
            self.log.info("Find project %s %s" % (dp, dv))
            node_child = self.processProjectVersion(dp, dv,
                                                    graph=graph_el['deps'])

            if node_parent and node_child and \
                    self.mConfDBReadOnly.nodesHaveRelationship(node_parent,
                                                               node_child,
                                                               "REQUIRES"):
                self.log.info(
                    "Pre-existing dependency (%s, %s)-["
                    ":REQUIRES]->(%s, %s)" % (proj, ver, dp, dv))
            else:
                self.log.info(
                    "Will add dependency (%s, %s)-[:REQUIRES]->(%s, %s)" % (
                        proj, ver, dp, dv))
        graph.append(graph_el)

        if graph == self.graph:
            self.mConfDB.createBulkPV(json.dumps(graph))
        return node_parent

    def processProjectVersion(self, p, v, sourceuri=None, graph=None):
        """
        Main entry point for the importer
        Processes the import of a project version.
        It starts with the top project imported and recursively builds a local
        representations of the dependencies graph that needs to be imported
        If the pair project version is the top element of the local graph, it
        sends a bulk update command to SoftConfDB instance

        :param p: the project name
        :param v: the version of the project
        :param alturi: the alternative URI for the source URI
        :param graph: local representations of the dependecies graph of the all
                      imported projects
        :return: the top project imported node instance
        """
        if graph is None:
            graph = self.graph
        # Cleanup the project name and version and get the SVN URL
        (proj, ver) = importerTranslateProject(p, v)
        tagpath = ""

        # If not forced check in the DB what the source URI should be
        forcedSourceURI = False
        if sourceuri is None:
            sourceuri = self.mConfDBReadOnly.getSourceURI(p, v)
        else:
            forcedSourceURI = True
            # Only in this case we need to save it in the project/version node

        self.log.info("%s/%s - Using import URI: %s" % (p, v, sourceuri))

        # Now checking whether we should get the info from SVN of GIT
        gitlab = self.inGitlab(proj, alturi=sourceuri)
        if gitlab:
            # In this case use the new code
            # This should be cleanup up but in the transition period
            # we'll use this hack
            self.log.info("Project %s is in Gitlab URI:%s" % (
                proj, sourceuri))
            return self.gitlabProcessProjectVersion(
                p, v, alturi=sourceuri, saveURIinPV=forcedSourceURI,
                graph=graph)

        # Only LCG/LCGCMT should not be in gitlab
        if proj not in ["LCG", "LCGCMT"]:
            raise Exception("Error: project %s should be in gitlab" % proj)

        # Formatting the project name/version
        corver = ver
        if proj in ver:
            corver = ver.replace(proj + "_", "")
        proj = proj.upper()

        # Looking for the project version in the DB

        # NON GILTAB NODE CREATIN -> CAN GO TO BULK (Project, version)
        tmp = self.mConfDBReadOnly.findVersion(proj, ver)
        createNode = False
        node_parent = None

        # First checking if the node is there with the correct revision
        if len(tmp) != 0:
            node = tmp[0]
            node_parent = node
        # If the node does not exist just create it...
        else:
            createNode = True

        # Rename LCGCMT to LCG
        if createNode and proj == "LCGCMT":
            proj = "LCG"

        graph.append({
            'project': proj,
            'version': corver,
            'saveURIinPV': False,
            'createNode': createNode,
            'autorelease': self.mAutorelease,
            'mPlatforms': self.mPlatforms,
            'sourceuri': sourceuri,
            'deps': [],
        })

        # For LCG we check we don't have a LCGCMT node already...
        if createNode and proj == "LCG":
            tmplcgcmt = self.mConfDBReadOnly.findVersion("LCGCMT", corver)
            if len(tmplcgcmt) > 0:
                self.log.info(
                    "Found LCGCMT version %s instead of LCG" % corver)
                node_parent = tmplcgcmt[0]
            else:
                self.log.info("Will create project %s %s" % (proj, corver))
        if graph == self.graph:
            self.mConfDB.createBulkPV(json.dumps(graph))
        return node_parent
