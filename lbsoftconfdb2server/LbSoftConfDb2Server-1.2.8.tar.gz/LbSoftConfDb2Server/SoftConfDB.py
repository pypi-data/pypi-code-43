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
Main class for SoftCondDB. All the functions in SoftConfDB performs operations
on the neo4j database.
"""
import logging
from datetime import datetime

import os
import re
from LbSoftConfDb2Server.SoftConfDbPermission import readOnly, writeAllowed
from py2neo import Graph
from py2neo.ogm import RelatedTo, RelatedFrom

from LbSoftConfDb2Server.LbSoftConfDbObjects import ProjectVersion, Project, \
    Platform, Datapkg, DatapkgVersion
import json
from collections import Counter
from LbEnv import fixProjectCase


def versionKey(v):
    '''
    For a version string with numbers alternated by alphanumeric separators,
    return a tuple containing the separators and the numbers.

    For example:
    >>> versionKey('1.2.3')
    (1, '.', 2, '.', 3)
    >>> versionKey('v10r0')
    ('v', 10, 'r', 0)
    >>> versionKey('1.2-a')
    (1, '.', 2, '-a')

    :param v: the project version
    :return: a tuple containing the separators and the numbers
    '''

    v = re.findall(r'[-a-zA-Z_.]+|\d+', v)
    return tuple([int(x) if x.isdigit() else x for x in v])


def sortVersions(versionlist, reverse=False):
    """
    Version sorter
    :param versionlist: the list of versions to sort
    :param reverse: if true, return the reverse sorted list
    :return: sorted list of version
    """
    return sorted(versionlist, key=versionKey, reverse=reverse)


# Various utilities for connection management
def _get_pwd_from_sys():
    """
    Get the Neo4j password from the environment of from a file on disk
    :returns a username, password tuple for Neo4j connection
    """
    # First checking the environment
    res = os.environ.get("NEO4JPWD", None)

    # Checking for the password in $HOME/private/neo4j.txt
    if res is None:
        fname = os.path.join(os.environ["HOME"], "private", "neo4j.txt")
        if os.path.exists(fname):
            with open(fname, "r") as f:
                data = f.readlines()
                if len(data) > 0:
                    res = data[0].strip()
    if res is None:
        # At this point we should have found the authentication
        # Otherwise, we throw an exception...
        raise Exception("Could not locate server credentials")

    # Separate the username/password
    (username, password) = res.split("/")
    return username, password


def get_connection(host=None,
                   username=None, passwd=None,
                   port=7687):
    """
    Create a connection to Neo4j
    :param host: the Neo4j server hostname
    :param username: the Neo4j server username
    :param passwd: the Neo4j server password
    :param port: the Neo4j server port
    """
    envhost = os.environ.get("NEO4JHOST", None)
    if envhost:
        host = envhost
    if host is None:
        host = "lbsoftdb.cern.ch"
    if os.environ.get("NEO4JPORT", None):
        port = os.environ.get("NEO4JPORT")

    if username is None or passwd is None:
        (username, passwd) = _get_pwd_from_sys()

    return "bolt://%s:%s@%s:%s/db/data/" % (username, passwd, host, port)


class SoftConfDB():
    """
    Main class interfacing to the LHCb Configuration Database
    """

    def __init__(self, dbConnectStr=None, logger=None):
        """
        Initialize the class, setting the address of the Database
        :param dbConnectStr: custom connection string for neo4j server
        """
        if not logger:
            self.log = logging.getLogger()
        else:
            self.log = logger
        if dbConnectStr is None:
            dbConnectStr = get_connection()
        # Initialize with the server address
        self.log.debug("Connecting to Neo4j DB: %s" % dbConnectStr)

        # Initializing the DB itself
        self.mNeoDB = Graph(dbConnectStr)

    def getPVFromString(self, node):
        """
        Converts a par of project_version to a neo4j project-version node
        :param node: the string representing the node
        :return: the neo4j node
        """
        if isinstance(node, str):
            tmp = node.split('_')
            return self.getPV(tmp[0], tmp[1])
        return node

    # Methods to query the database
    ###########################################################################
    @readOnly
    def listProjects(self, with_extra=False):
        """
        List the projects known by the SoftConfDB
        :param with_extra: flag to include the source uri in the list
        :return: list of projects
        """

        if with_extra:
            return [(a.name,
                     a.sourceuri) for a in Project.match(self.mNeoDB)]
        return [a.name for a in Project.match(self.mNeoDB)]

    @readOnly
    def getProjectNode(self, project):
        """
        return the node for a specific project
        :param project: the project name as a string
        :return: the neo4j project node
        """
        project = project.upper()
        return Project.match(self.mNeoDB, project).first()


    @readOnly
    def listDatapkgs(self):
        """
        List the datapackages known by the SoftConfDB
        :return: the list of datapackages database
        """
        return list(set([m.name for m in Datapkg.match(self.mNeoDB)]))

    @readOnly
    def listApplications(self):
        """
        List the applications known by the SoftConfDB
        :return: the list of applications in the neo4j database
        """
        query = "MATCH (n:Application) return distinct " \
                "n.name as project_name"
        res = self.mNeoDB.run(query).data()
        return [m['project_name'] for m in res]

    @readOnly
    def listReleaseReqs(self):
        """
        List the projects to be released
        :return: list of rojects to be released in the neo4j database
        """
        query = "MATCH (n:ToRelease) return n.project_name as project_name, " \
                "n.version as version"
        res = self.mNeoDB.run(query).data()
        return [(m['project_name'], m['version']) for m in res]

    @readOnly
    def listBuildToolProjects(self, buildtool):
        """
        List the projects using the specific buildtool
        :param buildtool: the buildtool to be used in the query
        :return: list of projects using the specific buildtool in the neo4j db
        """
        return [(m.project_name, m.version)
                for m in ProjectVersion.match(self.mNeoDB).where(
                buildTool=buildtool)
                ]

    @readOnly
    def listCMakeBuiltProjects(self):
        """
        List the projects using the CMAKE buildtool
        :return: list of projects using the CMAKE buildtool in the neo4j db
        """
        return self.listBuildToolProjects("CMAKE")

    @readOnly
    def listTag(self, tag):
        """
        List the applications in the database with a specific tag
        :param tag: the tag to be used in the query
        :return: ist of projects with the tag in the neo4j db
        """
        query = "MATCH (n:ProjectVersion) WHERE " \
                "ANY(item IN n.tags WHERE item = '%s') " \
                "return n.project_name as project_name, " \
                "n.version as version" % tag
        return_List = []
        res = self.mNeoDB.run(query).data()
        return_List.extend([(m['project_name'], m['version'], None)
                            for m in res])
        query = "MATCH (n:ProjectVersion)-[r:PLATFORM]->(q:Platform) WHERE " \
                "ANY(item IN r.tags WHERE item = '%s') " \
                "return n.project_name as project_name, " \
                "n.version as version, q.name as platform" % tag
        res = self.mNeoDB.run(query).data()
        return_List.extend([(m['project_name'], m['version'], m['platform'])
                            for m in res])
        return return_List

    @readOnly
    def listCMTBuiltProjects(self):
        """
        List the projects using the CMT buildtool
        :return: list of projects using the CMT buildtool in the neo4j db
        """
        return self.listBuildToolProjects("CMT")

    @readOnly
    def listReleaseStacks(self):
        """
        Returns the stack of the projects versions to be released
        :return: the stack of the projects versions to be released
        """
        self.log.debug("Starting listReleaseStacks")
        # First, find the top of the various stacks
        query = "MATCH p=(u:ToRelease)- [:REQUIRES*0..]->(v:ToRelease) WHERE" \
                " not (:ToRelease)-[:REQUIRES] ->(u:ToRelease) and not " \
                "(v:ToRelease)-[:REQUIRES]->(:ToRelease) WITH " \
                "extract(x in nodes(p)| x.name) as in_path_list, u, v " \
                "UNWIND in_path_list as in_path WITH in_path, u, v " \
                "OPTIONAL MATCH (:ProjectVersion{name:in_path})" \
                "-[:REQUIRES]->(m)-[:PLATFORM]->(q) WITH in_path, u, v, q, " \
                "m " \
                "OPTIONAL MATCH (:ProjectVersion{name:in_path})-" \
                "[:REQUESTED_PLATFORM]->(plat:Platform) RETURN DISTINCT " \
                "u.project_name as top_stack_project, u.version as " \
                "top_stack_version, v.project_name as bottom_stack_project, " \
                "v.version as bottom_stack_version, in_path as in_path, " \
                "q.name as children_platforms, plat.name as " \
                "requested_platforms, u.buildTool as build_tool " \
                "ORDER BY u.project_name, u.version"
        raw_data = {}
        # The results from the database in this format:
        # top_stack_project	top_stack_version	bottom_stack_project	bottom_stack_version	in_path	             children_platforms	    requested_platforms	    build_platform # nopep8
        # ALIGNMENT"	    "v9r0"	            "LHCB"	                "v34r2"	                "ALIGNMENT_v9r0"	 "i686-slc5-gcc43-opt"	null	                CMAKE # nopep8
        # ALIGNMENT"	    "v9r0"	            "LHCB"	                "v34r2"	                "ALIGNMENT_v9r0"	 "i686-slc5-gcc43-dbg"	null	                CMAKE # nopep8
        # ALIGNMENT"	    "v9r0"	            "LHCB"	                "v34r2"	                "LBCOM_v12r2"	     "i686-slc5-gcc43-dbg"	"i686-slc5-gcc43-dbg"	CMAKE # nopep8
        # We need to aggregate this db output in a dictionary:
        # "ALIGNMENT_v9r0" : {
        #        "path" : [
        #           "ALIGNMENT_v9r0" {
        #               "platforms" : ["i686-slc5-gcc43-opt", ...]
        #               "requested_platforms": [ "i686-slc5-gcc43-opt" ...]
        #               "build_tool" : "CMAKE"
        #           },
        #           "LBCOM_v12r2"{...
        #           }
        #           "PHYS_v14r2"{...
        #           }
        #       ]
        for line in self.mNeoDB.run(query).data():
            top_project = "%s_%s" % (line['top_stack_project'],
                                     line['top_stack_version'])
            if top_project not in raw_data.keys():
                raw_data[top_project] = {
                    'path': {}
                }
            if line['in_path'] not in raw_data[top_project]['path']:
                new_path = {
                    'platforms': set(),
                    'requested_platforms': set(),
                    'build_tool': set()
                }
                if line['build_tool']:
                    new_path['build_tool'].add(line['build_tool'])
                raw_data[top_project]['path'][line['in_path']] = new_path
            path = raw_data[top_project]['path'][line['in_path']]
            if line['children_platforms']:
                path['platforms'].add(line['children_platforms'])
            if line['requested_platforms']:
                path['requested_platforms'].add(line['requested_platforms'])
        # We transform the aggregated dictionary by computing the platforms
        # for each stack = &(all released children projects) &
        # &(all requested platforms)
        # "ALIGNMENT_v9r0" : {
        #        "path" : [ "ALIGNMENT_v9r0", LBCOM_v12r2, PHYS_v14r2]
        #        "platforms" : ["i686-slc5-gcc43-opt" ...]
        #         "build_tool" : "CMAKE"
        #       }
        for top_plat in raw_data.keys():
            stack = raw_data[top_plat]
            platforms = set()
            requested_platforms = set()
            build_tool = None
            for project_name in stack['path'].keys():
                project = stack['path'][project_name]
                if len(project['build_tool']):
                    if build_tool is None:
                        build_tool = project['build_tool']
                    build_tool &= project['build_tool']
                if len(project['platforms']):
                    if not len(platforms):
                        platforms = project['platforms']
                    else:
                        platforms &= project['platforms']
                if len(project['requested_platforms']):
                    if not len(requested_platforms):
                        requested_platforms = project['requested_platforms']
                    else:
                        requested_platforms &= project['requested_platforms']
            if build_tool is None or len(build_tool) != 1:
                build_tool = set(["CMAKE"])
            stack['build_tool'] = build_tool
            stack['path'] = set([tuple(x.split('_'))
                                 for x in stack['path'].keys()])
            stack['platforms'] = platforms
            if not len(platforms):
                stack['platforms'] = requested_platforms
            elif len(requested_platforms):
                stack['platforms'] &= requested_platforms
        # Now filter all the stacks
        filteredstacks = []
        for _, stack in raw_data.items():
            s = stack['path']
            ismerged = False
            for i, filtered_stack in enumerate(filteredstacks):
                fs = filtered_stack['path']
                intersec = s & fs
                if len(intersec) > 0:
                    union = s | fs
                    # Make sure we don't have the same project with two
                    # different versions
                    # This is not suported by the nightlies
                    duplicateProjs = [x for x, y in Counter(
                        [p for (p, v) in union]).items() if y > 1]
                    # If there are no duplicate projects, we can use the
                    # union of the stacks
                    if len(duplicateProjs) == 0:
                        # As discussed with mclemencic, we take the most
                        # restrictive platforms list
                        filteredstacks[i]['platforms'] &= stack['platforms']
                        filteredstacks[i]['path'] = union
                        filteredstacks[i]['build_tool'] &= stack['build_tool']
                        ismerged = True
                    break
            if not ismerged:
                filteredstacks.append(stack)

        # Filter output to remove sets not liked by XMLRPC
        for stack in filteredstacks:
            stack['path'] = list(stack['path'])
            stack['platforms'] = list(stack['platforms'])
            stack['build_tool'] = list(stack['build_tool'])
            if len(stack['build_tool']) != 1:
                stack['build_tool'] = "CMAKE"
            else:
                stack['build_tool'] = stack['build_tool'][0]
        return filteredstacks

    @readOnly
    def listVersions(self, project):
        """
        Lists the number of versions known for a given project
        :param project: the project to use in the query
        :return: Lists the number of versions
        """
        return [(a.project_name, a.version)
                for a in self.getProjectNode(project).project]

    @readOnly
    def listDatapkgVersions(self, datapkg):
        """
        Lists the number of versions known for a given datapkg
        :param project: the datapkg to use in the query
        :return: Lists the number of versions
        """
        datapkg = datapkg.upper()
        return list(set([(m.datapkg_name, m.version)
                         for m in DatapkgVersion.match(
                self.mNeoDB).where(
                datapkg_name=datapkg).order_by('_.version')]))

    @readOnly
    def findVersion(self, project, version, serialized=True):
        """
        Find whether a specific project version exists in the DB
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: neo4j node as a list (keeping the same api)
        """
        node = self.getPV(project, version)
        if node is None:
            return []
        if serialized:
            return [str(node)]
        else:
            return [node]

    @readOnly
    def listStackPlatformsRequestedForRelease(self, project, version):
        """
        In case some platforms have been explicitely requested for release,
        (adding the REQUESTED_PLATFORM link), list such platforms
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: list of platforms
        """
        project = project.upper()
        pv = self.getPV(project, version)
        return set([el.name for el in pv.requested_platform])

    @readOnly
    def listStackPlatformsToRelease(self, project, version):
        """
        Return the platforms for which we should release a project
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: the list of platforms
        """
        project = project.upper()
        query = "MATCH (n:ProjectVersion{name:\"%s_%s\"})-[:REQUIRES]->" \
                "(m)-[:PLATFORM]->(q) " \
                "RETURN distinct q.name as platform, " \
                "m.project_name as project, m.version as version" % \
                (project, version)
        plist = [(el['platform'], el['project'], el['version'])
                 for el in self.mNeoDB.run(query).data()]
        if len(plist) == 0:
            return []
        # Now grouping the platforms by project/version
        platinfo = {}
        for (plat, p, v) in plist:
            idx = "%s_%s" % (p, v)
            if idx not in platinfo:
                platinfo[idx] = set()
            platinfo[idx].add(plat)
        # Now taking the intersection
        curplat = None
        for plats in platinfo.values():
            if curplat is None:
                curplat = plats
            else:
                curplat = curplat & plats

        # And return the result
        return list(curplat)

    @readOnly
    def listAllPlatforms(self):
        """
        List all the Platforms known to the system
        :return: the list of platforms
        """
        return list(set([a.name for a in Platform.match(self.mNeoDB)]))

    @readOnly
    def listPlatforms(self, project, version, reltype="PLATFORM"):
        """
        List the Platforms released for a Couple project version
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param reltype: the relation type: PLATFORM or REQUESTED_PLATFORM
        :return: the list of platforms
        """
        return list(set([a.name for a in getattr(self.getPV(project, version),
                                                 reltype.lower())]))

    @readOnly
    def listDependencies(self, project, version):
        """
        List the project/versions the specified project depends on
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: the list of dependencies
        """
        project = project.upper()
        query = "MATCH (n:ProjectVersion{name:\"%s_%s\"})-[:REQUIRES*]->(m) " \
                "RETURN DISTINCT " \
                "m.project_name as project, m.version as version" % \
                (project, version)
        res = [(el['project'], el['version'])for el in
               self.mNeoDB.run(query).data()]
        return res

    def _processRels(self, query):
        """
        internal function to cache the relations in a query
        :param query: the query to be executed in neo4j
        :return: the list of cached relationships
        """
        relationship_set = set()
        all_rels = [r['rel'] for r in self.mNeoDB.run(query).data()]
        for rels in all_rels:
            for r in rels:
                p_start = r.start_node
                p_end = r.end_node
                relationship_set.add(((str(p_start["project_name"]),
                                       str(p_start["version"])),
                                      (str(p_end["project_name"]),
                                       str(p_end["version"]))))
        return list(relationship_set)

    @readOnly
    def listDependencyRelations(self, project, version):
        """
        List the relationships the specified project depends on
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: List the relationships the specified project depends on
        """
        project = project.upper()
        query = "MATCH p = (n:ProjectVersion{name:\"%s_%s\"})-[:REQUIRES*]" \
                "->(m) RETURN relationships(p) as rel" % \
                (project, version)
        return self._processRels(query)

    @readOnly
    def listReferencesRelations(self, project, version):
        """
        List the relationships the specified project depends on
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: List the relationships the specified project depends on
        """
        project = project.upper()
        query = "MATCH p = (m)-[:REQUIRES*]->(n:ProjectVersion{" \
                "name:\"%s_%s\"}) RETURN relationships(p) as rel" % \
                (project, version)
        return self._processRels(query)

    def _processRelAsDot(self, pvlist, caller, name):
        """
        Converts the a list of relatiship into dot file
        :param pvlist: the list project-versions nodes
        :param caller: the function that shoud be used to get the nodes
                       relations
        :param name: the name for the dot graph
        :return: the dot graph fo the lists of nodes.
        """
        alldeps = set()
        for (project, version) in pvlist:
            for p in caller(project, version):
                ((p1, v1), (p2, v2)) = p
                alldeps.add(p)

        out = "digraph %s {\n" % name
        for ((p1, v1), (p2, v2)) in sorted(alldeps):
            out += "%s_%s -> %s_%s\n" % (p1, v1, p2, v2)
        out += "}"
        return out

    @readOnly
    def getDependenciesAsDot(self, pvlist, name="software_deps"):
        """
        Get the Dot file with the dependencies of a given project
        :param pvlist: the list project-versions nodes
        :param name: the name for the dot graph
        :return: the graph of dependencies in dot format
        """
        return self._processRelAsDot(pvlist,
                                     self.listDependencyRelations, name)

    @readOnly
    def getReferencesAsDot(self, pvlist, name="software_deps"):
        """
        Get the Dot file with the dependencies of a given project
        :param pvlist: the list project-versions nodes
        :param name: the name for the dot graph
        :return: the graph of references in dot format
        """
        return self._processRelAsDot(pvlist,
                                     self.listReferencesRelations, name)

    @readOnly
    def listReferences(self, project, version):
        """
        List the project/versions that depend on this project
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: List of project/versions that depend on this project
        """
        project = project.upper()
        query = "MATCH (m)-[:REQUIRES*]->(n:ProjectVersion{name:\"%s_%s\"}) " \
                "RETURN m.project_name as project, m.version as version" % \
                (project, version)
        res = [(el['project'], el['version']) for el in
               self.mNeoDB.run(query).data()]
        return res

    @readOnly
    def listActiveReferences(self, project, version):
        """
        List the project/versions that depend on this project,
        that are active on disk
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: List of project/versions that depend on this project
                 that are active on disk
        """
        project = project.upper()
        query = "MATCH (m:Active)-" \
                "[:REQUIRES*]->(n:ProjectVersion{name:\"%s_%s\"}) " \
                "RETURN m.project_name as project," \
                " m.version as version" % (project, version)
        res = [(el['project'], el['version']) for el in
               self.mNeoDB.run(query).data()]
        return res

    @readOnly
    def show(self, project, version):
        """
        Show the various attributes of a project/version
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: a string with all the information about the project version
                 node
        """
        node_pv = self.getPV(project, version)

        ret = ""
        ret += "Node %s Properties\n" % node_pv.ID
        ret += "------------------------------\n"
        for (p, v) in sorted(node_pv.get_properties().items()):
            ret += "%-20s: %s\n" % (p, v)

        ret += "\nNode %s Labels\n" % node_pv.ID
        ret += "------------------------------\n"
        labels = node_pv.get_labels()
        for label in sorted(labels.keys()):
            ret += "%-20s: %s\n" % (label, labels[label])


        ret += "\nNode %s relationships\n" % node_pv.ID
        ret += "------------------------------\n"
        outrels = node_pv.get_relationships(RelatedTo)
        for r in outrels:
            relprops = r.end_node.get_properties()
            relprops['ID'] = r.end_node.ID
            props = ", ".join(
                "{}:{}".format(str(k), str(v)) for k, v in sorted(
                    relprops.items()))
            tmp = "%-15s -> (%s)\n" % (r.type + "(O)", props)
            ret += tmp
        inrels = node_pv.get_relationships(RelatedFrom)
        for r in inrels:
            relprops = r.start_node.get_properties()
            relprops['ID'] = r.start_node.ID
            props = ", ".join(
                "{}:{}".format(str(k), str(v)) for k, v in sorted(
                    relprops.items()))
            tmp = "%-15s <- (%s)\n" % (r.type + "(I)", props)
            ret += tmp
        return ret

    @readOnly
    def showProject(self, project):
        """
        Show the project properties
        :param project: the project to use in the query
        :return: a string with all the information about the project node
        """
        node = self.getProjectNode(project)
        if not node:
            return None
        ret = "Node %s Properties\n" % node.ID
        ret += "------------------------------\n"
        for (p, v) in sorted(node.get_properties().items()):
            ret += "%-30s: %s\n" % (p, v)
        return ret

    @readOnly
    def nodesHaveRelationship(self, parent, child, type):
        """
        Check if the nodes have a directed parent to child node
        of given type
        :param parent: the parent node (string or py2neo node)
        :param child: the child node (string or py2neo node)
        :param type: the type of relationship
        :return: true if there is a relationship of this type from the parent
                 to the child, false otherwise
        """
        parent = self.getPVFromString(parent)
        child = self.getPVFromString(child)
        outrels = parent.get_relationships(RelatedTo)
        for r in outrels:
            if r.end_node.ID == child.ID and r.type == type:
                return True
        return False

    @readOnly
    def listActive(self):
        """
        List the active project/versions
        :return: list of tuple project-version of nodes that are active
        """
        query = "MATCH (n:Active) return distinct " \
                "n.project_name as project_name, n.version as project_version"
        res = self.mNeoDB.run(query).data()
        return [(m['project_name'], m['project_version']) for m in res]

    @readOnly
    def listActiveApplications(self):
        """
        List the active project/versions applications
        :return: list of tuple project-version of applications
                 nodes that are active
        """
        query = "MATCH (m:Application)-[:PROJECT]->(n:Active) return " \
                "distinct " \
                "n.project_name as project_name, n.version as project_version"
        res = self.mNeoDB.run(query).data()
        return [(m['project_name'], m['project_version']) for m in res]

    @readOnly
    def listUsed(self):
        """
        List the used project/versions
        :return: list of tuple project-version of used
                 nodes that are active
        """
        query = "MATCH (n:Used) return distinct " \
                "n.project_name as project_name, n.version as project_version"
        res = self.mNeoDB.run(query).data()
        return [(m['project_name'], m['project_version']) for m in res]

    @readOnly
    def checkUnused(self, verbose):
        """
         List the unused project/versions
        :param verbose:
        :return: list of tuple project-version of unused
                 nodes that are active
        """
        queryappused = "MATCH (n:Used) WHERE n:Active  return distinct " \
                       "n.project_name as project_name, " \
                       "n.version as project_version"
        queryused = "MATCH (n:Used)-[:REQUIRES*]->(m) " \
                    "WHERE n:Active  return distinct " \
                    "m.project_name as project_name, " \
                    "m.version as project_version"

        active = self.listActive()
        res = self.mNeoDB.run(queryappused).data()
        appused = [(m['project_name'], m['project_version']) for m in res]
        res = self.mNeoDB.run(queryused).data()
        used = [(m['project_name'], m['project_version']) for m in res]

        activec = []
        for n in active:
            activec.append((n[0], n[1]))
            if verbose:
                print("Active: %s %s" % (n[0], n[1]))

        usedc = []
        for n in used:
            usedc.append((n[0], n[1]))
            if verbose:
                print("Used: %s %s" % (n[0], n[1]))

        appusedc = []
        for n in appused:
            appusedc.append((n[0], n[1]))
            if verbose:
                print("AppUsed: %s %s" % (n[0], n[1]))

        if verbose:
            print("Unused = Active - Used - AppUsed")
        return [n for n in activec if n not in usedc and n not in appusedc]

    @readOnly
    def getBuildTools(self, project, version):
        """
        Check which buildtool should used to build this project
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: the buildtool used for the project/version as list
                 (for backwards compatibility)
        """
        project = project.upper()

        # First checking whether we're directly connected to the node
        node_pv = self.getPV(project, version)
        if node_pv.buildTool is not None:
            return [node_pv.buildTool]

        # Or if one of the ancestors
        query = "MATCH (n:ProjectVersion{name:\"%s_%s\"})-[:REQUIRES*]->(m)" \
                " RETURN DISTINCT m.buildTool as buildTool" % \
                (project, version)
        plist = [el['buildTool'] for el in self.mNeoDB.run(query).data()
                 if el['buildTool']]
        return plist

    # Methods to add/update nodes
    ###########################################################################

    @writeAllowed
    def addPVPlatform(self, project, version, platform, reltype="PLATFORM"):
        """
        Adds a link from a project version to a platform
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param platform: the platform to use in the query
        :param reltype: The relationship type to be added
        """
        """ Get the dependencies for a single project """
        project = project.upper()
        node_pv = self.getPV(project, version)
        if not node_pv:
            node_pv = self.createPV(project, version)
        node_platform = Platform(platform)
        if reltype != 'PLATFORM':
            childre_platforms = set([y.name for x in node_pv.requires
                                     for y in x.platform])
            if len(childre_platforms) and platform not in childre_platforms:
                raise Exception(
                    "%s platform is not in the set of chidlren "
                    "platforms: %s" % (platform, childre_platforms))
        self.mNeoDB.push(node_platform)
        getattr(node_pv, reltype.lower()).add(node_platform)
        self.mNeoDB.push(node_pv)

    @writeAllowed
    def delPVPlatform(self, project, version, platform, reltype="PLATFORM"):
        """
        Deletes a link from a project version to a platform
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param platform: the platform to use in the query
        :param reltype: The relationship type to be deleted
        """
        node_pv = self.getPV(project, version)
        if node_pv is None:
            self.log.debug("Node not found, exiting")
            return
        remov_obj = None
        for node_platform in getattr(node_pv, reltype.lower()):
            if node_platform.name == platform:
                self.log.debug("Removing relationship: %s" %
                                 str(node_platform))
                remov_obj = node_platform
        if remov_obj is None:
            self.log.debug("No relation was found, exiting")
            return
        getattr(node_pv, reltype.lower()).remove(remov_obj)
        self.mNeoDB.push(node_pv)

    @writeAllowed
    def versionIsPattern(self, version):
        """
        Verifies if a version is a pattern
        :param version: the version to check
        :return: True if the version is a pettern, False otherwise
        """
        return '*' in version

    @writeAllowed
    def createProjectNode(self, project, sourceuri=None):
        """
        Create a project node, with appropriate links
        :param project: the project to use in the query
        :param sourceuri: the source uri in gitlab where the project is saved
        :return: the project node
        """
        """  """
        project = project.upper()
        project_db = self.getProjectNode(project)
        if not project_db:
            project_db = Project(project, sourceuri=sourceuri)
            self.mNeoDB.push(project_db)
        else:
            raise Exception("Project %s already exists in the database" %
                            project)
        return project_db

    @writeAllowed
    def createPVSerializable(self, project, version):
        """
        Serialized verison of createPV in order to be used in the XMLRPC
        server
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: a string representation to the project version
        """
        return str(self.createPV(project, version))

    @writeAllowed
    def createProjectSerializable(self, project, sourceuri):
        """
        Serialized verison of createProject in order to be used in the XMLRPC
        server
        :param project: the project to use in the query
        :return: a string representation to the project version
        """
        return str(self.createProjectNode(project, sourceuri=sourceuri))

    @writeAllowed
    def createBulkPV(self, data):
        """
        Creat or get the top node of a bulk insert
        :param data: json string of a bulk insert of nodes and their
                     dependecies
        :return: the top ndoe of the bulk insert
        """
        data = json.loads(data)
        if len(data) > 0:
            data = data[0]
            return str(self._insertPVFromBulk(data['project'],
                                              data['version'],
                                              data['saveURIinPV'],
                                              data['deps'],
                                              data['autorelease'],
                                              data['mPlatforms'],
                                              data.get('sourceuri', None),
                                              commitID=data.get('commitID',
                                                                None)
                                              ))
        return None

    def _insertPVFromBulk(self, proj, ver, saveURIinPV, deps, autorelease,
                          mPlatforms, sourceuri, commitID=None):
        """
        Inserts into the neo4j db a a node from a bulk list of the project
        versions

        :param proj: the project to use in the query
        :param ver: the version to use in the query
        :param saveURIinPV: flag to mark if the function should save the uri
                            in the project version node
        :param deps: the list of dependencies for the node
        :param autorelease: flag to mark if the function should autorelease the
                            node
        :param mPlatforms: a list of platforms that are requested in the bulk
                           release
        :param sourceuri: the source uri in gitlab where the project is saved
        :return: the neo4j node
        """
        tmp = self.findVersion(proj, ver, serialized=False)
        if len(tmp) == 0:
            node_parent = self.createPV(proj, ver, commitID=commitID)
            if saveURIinPV:
                self.setPVProperty(proj, ver, "sourceuri", sourceuri)
            # If releasing is needed!
            if autorelease and proj.upper() not in ["LCG", "LCGCMT"]:
                self.log.debug("Requesting release of %s %s" % (proj, ver))
                self.setReleaseFlag(proj, ver)
                if mPlatforms:
                    for p in mPlatforms:
                        self.addPVPlatform(proj, ver, p, "REQUESTED_PLATFORM")
        else:
            node_parent = tmp[0]

        # If a node already exists but the gitlab data has a different commitID
        # (after a retag), the node commitID is updated with the new commitID
        #  and all the existing links to the dependencies (created for the old
        #  commitID) that are not present in the list of the dependencies for
        #  the  new commitID are removed.

        if node_parent.commitID != commitID:
            # Update the node after retagging
            self.log.warning("The commit ID for the project %s with the "
                             "version %s changed from %s to %s. Updating the "
                             "node and its dependencies "
                             "into the database" % (node_parent.project_name,
                                                    node_parent.version,
                                                    node_parent.commitID,
                                                    commitID))
            node_parent.commitID = commitID
            deps_pv_names = ["%s_%s" % (dep['project'].upper(),
                                        dep['version']) for dep in deps]
            to_remove = []
            for dep in node_parent.requires:
                if dep.name not in deps_pv_names:
                    to_remove.append(dep)
            for tmp in to_remove:
                node_parent.requires.remove(tmp)
            self.mNeoDB.push(node_parent)

        for dep in deps:
            node_child = self._insertPVFromBulk(dep['project'],
                                                dep['version'],
                                                dep['saveURIinPV'],
                                                dep['deps'],
                                                dep['autorelease'],
                                                dep['mPlatforms'],
                                                dep.get('sourceuri', None),
                                                commitID=dep.get('commitID',
                                                                 None))
            # Now checking if the links exist
            if not self.nodesHaveRelationship(node_parent, node_child,
                                              "REQUIRES"):
                self.addRequires(node_parent, node_child)
        # Don't forget to add the parent node rels to the DB.
        self.mNeoDB.push(node_parent)
        return node_parent

    @writeAllowed
    def createPV(self, project, version, commitID=None):
        """
        Create a project version node, with appropriate links
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: the project version node
        """
        # Check whether the version is a pattern
        # If yes, then create the appropriate node
        if self.versionIsPattern(version):
            return self.createVersionPattern(project, version,
                                             commitID=commitID)
        parent_node = self.getProjectNode(project)
        if not parent_node:
            parent_node = self.createProjectNode(project)
        project_version = self.getPV(project, version)
        if not project_version:
            project_version = ProjectVersion(project, version,
                                             commitID=commitID)
        else:
            raise Exception("Project %s with version %s already exists " %
                            (project, version))
        project_version.project.add(parent_node)

        self.mNeoDB.push(project_version)

        self._updateVersionPatternLinks(project_version)
        return project_version

    @readOnly
    def getPV(self, project, version):
        """
        Get a project version node
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: the project version node
        """
        project = project.upper()

        return ProjectVersion.match(self.mNeoDB,
                                    "%s_%s" % (str(project).upper(),
                                               version)).first()

    @writeAllowed
    def deletePV(self, project, version):
        """
        Deletes a project version node
        :param project: the project to use in the query
        :param version: the version to use in the query
        """
        project = project.upper()
        self.log.debug("Deleting: %s %s" % (project, version))
        node_pv = self.getPV(project, version)
        if node_pv is None:
            self.log.debug("Node not found, exiting")
            return
        self.mNeoDB.delete(node_pv)

    @writeAllowed
    def createVersionPattern(self, project, version, commitID=None):
        """
         Create a project version pattern, with appropriate links
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: the project version node
        """
        parent_node = self.getProjectNode(project)
        if not parent_node:
            parent_node = self.createProjectNode(project)
        project_version = self.getPV(project, version)
        if not project_version:
            project_version = ProjectVersion(project, version,
                                             commitID=commitID)
        else:
            raise Exception("Project %s with version %s already exists " %
                            (project, version))
        project_version.pattern.add(parent_node)
        project_version.patternVersion = True
        # Make sure the links point to the correct versions
        self._updateVersionPatternLinks(project_version)

        return project_version

    def _getLatestVersionForPattern(self, project_name, pattern):
        """
        Gets the latest version for a project against the give pattern
        :param project_name: the project to use in the query
        :param pattern: the pattern against the version of the project name
                        should be check against
        :return: the latest project version node that matches the pattern
        """
        query = "MATCH p=(u:ProjectVersion{project_name:'%s'}) " \
                "RETURN u.version as version" % project_name
        versions = []
        for line in self.mNeoDB.run(query).data():
            if not self.versionIsPattern(line['version']):
                versions.append(line['version'])
        matching = self.matchAndSortVersions(pattern,
                                             versions)
        if len(matching) == 0:
            self.log.debug("No match found for %s_%s pattern" % (
                project_name, pattern))
            return None
        return self.getPV(project_name, matching[-1])

    def _updateVersionPatternLinks(self, pv):
        """
        Update all the links between the version patterns and
        the actual project versions
        :param pv: the project version node
        """
        patterns = {}
        if self.versionIsPattern(pv.version):
            patterns[pv.version] = {
                'required_by': [],
                'match': self._getLatestVersionForPattern(pv.project_name,
                                                          pv.version)
            }
            query = "MATCH p=(u:ProjectVersion)- [:REQUIRES_PATTERN]->" \
                    "(v:PatternVersion{name:'%s'}) " \
                    "RETURN u.name as parent" % \
                    pv.name
            for line in self.mNeoDB.run(query).data():
                patterns[pv.version]['required_by'].append(line['parent'])
        else:
            query = "MATCH p=(u:ProjectVersion)- [:REQUIRES_PATTERN]->" \
                    "(v:PatternVersion{project_name:'%s'}) " \
                    "RETURN u.name as parent, v.version as pattern" % \
                    pv.project_name
            for line in self.mNeoDB.run(query).data():
                pattern = line['pattern']
                if not patterns.get(pattern, None):
                    patterns[pattern] = {
                        'required_by': [],
                        'match': self._getLatestVersionForPattern(
                            pv.project_name, pattern)
                    }
                patterns[pattern]['required_by'].append(line['parent'])
        for pattern in patterns.keys():
            self.log.debug("Processing pattern: %s_%s" % (pv.project_name,
                                                            pattern))
            for requiredBy in patterns[pattern]['required_by']:
                p, v = tuple(requiredBy.split('_'))
                pv_requiredBy = self.getPV(p, v)
                current_version = None
                for dep in pv_requiredBy.requires:
                    if dep.project_name == pv.project_name:
                        current_version = dep
                        break
                if current_version:
                    pv_requiredBy.requires.remove(current_version)
                if patterns[pattern]['match']:
                    pv_requiredBy.requires.add(patterns[pattern]['match'])
                self.mNeoDB.push(pv_requiredBy)

    @writeAllowed
    def deleteActiveLinks(self, batch=None):
        """ Delete the active nodes in the graph """
        active = self.listActive()
        for (proj, version) in active:
            pv = self.getPV(proj, version)
            pv.active = False
            self.mNeoDB.push(pv)

    @writeAllowed
    def deleteUsedLinks(self):
        """ Delete the used nodes in the graph """
        used = self.listUsed()
        for (proj, version) in used:
            pv = self.getPV(proj, version)
            pv.used = False
            self.mNeoDB.push(pv)

    @writeAllowed
    def setAllAppVersionsUsed(self):
        """ List the number of versions known for a given project """
        applications = self.listApplications()
        for app in applications:
            proj = self.getProjectNode(app)
            for pv in proj.project:
                pv.used = True
                self.mNeoDB.push(pv)

    @writeAllowed
    def setPVUsed(self, project, version):
        """
        Set the used link for a project version
        :param project: the project to use in the query
        :param version: the version to use in the query
        """
        pv = self.getPV(project, version)
        if pv is None:
            raise Exception("%s %s not found" % (project, version))
        pv.used = True
        self.mNeoDB.push(pv)

    @writeAllowed
    def setApplication(self, project):
        """
        Set the link to indicate that a project is an application
        :param project: the project to use in the query
        """
        project = self.getProjectNode(project)
        project.application = True
        self.mNeoDB.push(project)

    @writeAllowed
    def unsetApplication(self, project):
        """
        Unset the used link for a project version
        :param project: the project to use in the query
        """
        project = self.getProjectNode(project)
        project.application = False
        self.mNeoDB.push(project)

    @writeAllowed
    def setBuildTool(self, project, version, buildTool):
        """
        Set the link to indicate that a project was built with CMake
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param buildTool: the name of the buildtool to be be saved
        :return:
        """
        project = project.upper()
        if buildTool is None:
            buildTool = "CMAKE"
        node_pv = self.getPV(project, version)
        node_pv.buildTool = buildTool
        node_pv.buildToolDate = str(datetime.now())
        self.mNeoDB.push(node_pv)

    @writeAllowed
    def unsetBuildTool(self, project, version):
        """
        Unset the link to indicate that a project was built with CMake
        :param project: the project to use in the query
        :param version: the version to use in the query
        """
        project = project.upper()
        node_pv = self.getPV(project, version)
        node_pv.buildTool = None
        node_pv.buildToolDate = None
        self.mNeoDB.push(node_pv)

    @writeAllowed
    def setTag(self, project, version, tag):
        """
        Set the link to a node named tag from the given project/version
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param tag: the tag to be added
        """
        pv = self.getPV(project, version)
        if not pv:
            raise Exception("%s %s not found" % (project, version))
        props = pv.get_properties()
        existing_tags = props.get('tags', [])
        if tag in existing_tags:
            return
        existing_tags.append(tag)
        props['tags'] = existing_tags
        pv.set_properties(props)
        self.mNeoDB.push(pv)

    @writeAllowed
    def unsetTag(self, project, version, tag):
        """
        Unset the link to indicate that a project was built with CMake
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param tag: the tag to be removed
        :return:
        """
        pv = self.getPV(project, version)
        if not pv:
            raise Exception("%s %s not found" % (project, version))
        props = pv.get_properties()
        existing_tags = props.get('tags', [])
        new_tags = [x for x in existing_tags if x != tag]
        props['tags'] = new_tags
        pv.set_properties(props)
        self.mNeoDB.push(pv)

    @writeAllowed
    def setPlatformTag(self, project, version, platform, tag):
        """
        Set the link to a node named tag from the given project/version
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param platform: the platform to use in the query
        :param tag: the tag to be added
        """
        pv = self.getPV(project, version)
        if not pv:
            raise Exception("%s %s not found" % (project, version))
        platform = Platform.match(self.mNeoDB, str(platform)).first()
        tmp_data = pv.platform.get(platform, 'tags', [])
        tmp_data.append(tag)
        pv.platform.remove(platform)
        pv.platform.add(platform, {'tags': tmp_data})
        self.mNeoDB.push(pv)

    @writeAllowed
    def unsetPlatformTag(self, project, version, platform, tag):
        """
        Unset the link to indicate that a project was built with CMake
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param platform: the platform to use in the query
        :param tag: the tag to be removed
        """
        pv = self.getPV(project, version)
        if not pv:
            raise Exception("%s %s not found" % (project, version))
        platform = Platform.match(self.mNeoDB, str(platform)).first()
        tmp_data = pv.platform.get(platform, 'tags', [])
        new_tags = [x for x in tmp_data if x != tag]
        pv.platform.remove(platform)
        pv.platform.add(platform, {'tags': new_tags})
        self.mNeoDB.push(pv)

    @writeAllowed
    def setReleaseFlag(self, project, version):
        """
        Set the link to indicate that a release was requested
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return:
        """
        project = project.upper()
        node_pv = self.getPV(project, version)
        for children in node_pv.requires:
            if children.toRelease is False and not children.releasedDate:
                raise Exception("In order to mark project %s for release, "
                                "the required project %s needs to be makred "
                                "for release before" % (node_pv.name,
                                                        children.name))
        node_pv.toRelease = True
        self.mNeoDB.push(node_pv)

    @writeAllowed
    def unsetReleaseFlag(self, project, version, not_released=False):
        """
        Unset the link indicated that a release was requested
        Set not_released to true if a project version was accidental marked to
        be release
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param not_released: flag to mark if a project version was
                             accidental marked to be release
        """
        project = project.upper()
        node_pv = self.getPV(project, version)

        # Does not make sense if the node was not created
        if not node_pv:
            return
        if not not_released:
            node_pv.releasedDate = datetime.now()
        node_pv.toRelease = False
        self.mNeoDB.push(node_pv)

    @writeAllowed
    def setPVActive(self, project, version, batch=None):
        """
        Set the used link for a project version
        :param project: the project to use in the query
        :param version: the version to use in the query
        """
        pv = self.getPV(project, version)
        if pv is None:
            raise Exception("%s %s not found" % (project, version))
        pv.active = True
        self.mNeoDB.push(pv)

    @writeAllowed
    def matchAndSortVersions(self, pattern, vers):
        """
        Filters the version found to those matching the pattern
        and returns them sorted
        :param pattern: the patter to check for
        :param vers: a list of versions to check against
        :return: the sorted list of version
        """
        # Patterns are:
        # v* v1r* v1r2p* etc etc
        # We keep everything before the * and only keep the versions
        # that start by that...
        if '*' not in pattern:
            raise Exception("%s is not a valid pattern" % pattern)

        prefix = pattern.split("*")[0]
        return sorted([vi for vi in vers if vi.startswith(prefix)],
                      key=versionKey)

    @writeAllowed
    def addRequires(self, parentNode, childNode):
        """
        Add a dependency between two projects, which need to have been
        :param parentNode: the parent node that requires the child
        :param childNode: the child node that is required by the parent node
        """
        parentNode = self.getPVFromString(parentNode)
        childNode = self.getPVFromString(childNode)
        if self.versionIsPattern(childNode.version):
            parentNode.requiresPattern.add(childNode)
        else:
            parentNode.requires.add(childNode)
        self.mNeoDB.push(parentNode)
        self.mNeoDB.push(childNode)
        self._updateVersionPatternLinks(childNode)

    @writeAllowed
    def createDatapkgVersion(self, project, hat, datapkg, version):
        """
        Return or create a datapkg node
        :param project: the project name to use in the query
        :param hat: the hat of project to use in the query
        :param datapkg: the datapackage name
        :param version: the version of the datapackage
        :return: the datapackage as the neo4j node
        """
        project = project.upper()
        datapkgini = datapkg
        datapkg = datapkg.upper()
        if hat is None:
            hat = ""
        node_project = self.getProjectNode(project)
        if not node_project:
            node_project = self.createProjectNode(project)
        node_datapkg = Datapkg(datapkg, hat, datapkgini)
        node_datapkg.pkgproject.add(node_project)
        node_dv = DatapkgVersion(datapkg, version)
        self.mNeoDB.push(node_dv)
        node_datapkg.datapkg.add(node_dv)
        self.mNeoDB.push(node_datapkg)
        return node_dv

    # Methods to sets properties on Project nodes
    ###########################################################################
    @writeAllowed
    def setProjectProperty(self, project, name, value):
        """
        Set the properties of a given project
        :param project: the project to use in the query
        :param name: the name the property to set
        :param value: the value of the property to set
        """
        node = self.getProjectNode(project)
        if not node:
            return
        if name == "name":
            raise Exception("Cannot reset the name "
                            "property of a project node...")
        props = node.get_properties()
        props[name] = value
        # Now setting the properties
        node.set_properties(props)
        self.mNeoDB.push(node)

    @writeAllowed
    def resetProjectProperties(self, project):
        """
        Reset the properties of a given project
        Only keep the mandatory "project" one
        :param project: the project to use in the query
        """
        node = self.getProjectNode(project)
        if not node:
            return
        props = node.get_properties()
        for k in props.keys():
            if k != 'name':
                props[k] = None
        # Now setting the properties
        node.set_properties(props)
        self.mNeoDB.push(node)

    @readOnly
    def getProjectProperties(self, project):
        """
        Get the properties of a given project
        :param project: the project to use in the query
        :return: a dictionary of properties values
        """
        node = self.getProjectNode(project)
        if not node:
            return None
        props = node.get_properties()
        return props

    @readOnly
    def dumpAllProjectProperties(self):
        """
        Dump the properties of know projects
        :return: a dictionary of all the projectts properties with the project
                 name as the key
        """
        ret = {}
        for a in Project.match(self.mNeoDB):
            props = a.get_properties()
            ret[a.name] = props
        return ret

    PVMANDATORYPROPS = ["project_name", "name", "version"]

    @writeAllowed
    def setPVProperty(self, project, version, name, value):
        """
        Set the properties of a given project/version
        :param project: the project to use in the query
        :param version: the version to use in the query
        :param name: the name the property to set
        :param value: the value of the property to set
        """
        pv = self.getPV(project, version)
        if not pv:
            raise Exception("Cannot find %s %s" % (project, version))

        # Check we don't reset the project name itself
        if name in self.PVMANDATORYPROPS:
            raise Exception("Cannot reset the %s property of a "
                            "project/version node..." % name)
        props = pv.get_properties()
        props[name] = value
        # Now setting the properties
        pv.set_properties(props)
        self.mNeoDB.push(pv)

    @writeAllowed
    def resetPVProperties(self, project, version):
        """
        Reset the properties of a given project/version
        Only keep the mandatory "project/versions" ones
        :param project: the project to use in the query
        :param version: the version to use in the query
        """
        # Checking that the PV exists
        pv = self.getPV(project, version)
        if not pv:
            raise Exception("Cannot find %s %s" % (project, version))

        props = pv.get_properties()
        for k in props.keys():
            if k not in self.PVMANDATORYPROPS:
                props[k] = None
        # Now setting the properties
        pv.set_properties(props)
        self.mNeoDB.push(pv)

    @readOnly
    def getPVProperties(self, project, version):
        """
        Get the properties of a given project/version
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: the properties oof a the node as a dictionary
        """
        pv = self.getPV(project, version)
        if not pv:
            raise Exception("Cannot find %s %s" % (project, version))
        return pv.get_properties()

    @readOnly
    def getSourceURI(self, project, version):
        """
        Method to return the location at which a project can be found,
        using the SoftConfDB
        :param project: the project to use in the query
        :param version: the version to use in the query
        :return: the source uri of the project version
        """
        project = project.upper()
        sourceuri = None

        # First check whether theere is something defined
        # for the project version
        try:
            if version is not None:
                pvprops = self.getPVProperties(project, version)
                sourceuri = pvprops.get("sourceuri", None)
        except:
            # If there is no node for the project we just ignore
            self.log.debug(
                "No Project/Version found for %s %s" % (project, version))

        if sourceuri is None:
            # In this case check at the project level
            pprops = self.getProjectProperties(project)
            tmpuri = None
            if pprops is not None:
                tmpuri = pprops.get("sourceuri", None)
            if tmpuri is not None:
                sourceuri = tmpuri
                if version is not None:
                    sourceuri = "%s#%s" % (sourceuri, version)

        if sourceuri is None:
            # we still haven't managed looking into PV AND project nodes
            # we return the simplest URI...
            sourceuri = self._sanitizeProjectName(project)
            if version is not None:
                sourceuri = "%s#%s" % (sourceuri, version)

        return sourceuri

    def _sanitizeProjectName(self, pname):
        """
        Puts back the correct case in display
        :param pname: the name to sanitize
        :return: the sanitized name
        """
        return fixProjectCase(pname)
