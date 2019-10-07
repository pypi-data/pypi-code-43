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
Representation of the objects used in the py2neo Object Graph Mapping for
Neo4j
"""

from py2neo.ogm import GraphObject, Property, Label, RelatedTo, RelatedFrom, \
    RelatedObjects


class CaseInsensitiveProperty(Property):
    def __set__(self, instance, value):
        Property.__set__(self, instance, str(value).upper())


class LbRelationCacheObject(object):
    """
    Object used in OGM to cache relations between object
    """
    def __init__(self, start_node, end_node, id, type):
        self.start_node = start_node
        self.end_node = end_node
        self.ID = id
        self.type = type


class LbBaseGraphObject(GraphObject):
    """
    Base object for OGM objects. Extends py2neo GraphObject
    """
    @property
    def ID(self):
        return self.__node__.identity

    def get_properties(self):
        """
        Get the properties of a Node
        :return: the properties of the node
        """
        # needed to trigger the update of the __node__ from db
        getattr(self, self.__primarykey__)
        return {key: value for key, value in self.__node__.items() if
                hasattr(self, key)}

    def get_labels(self):
        """
        Get the labels of a Node
        :return: the properties of the node
        """
        # needed to trigger the update of the __node__ from db
        getattr(self, self.__primarykey__)
        labels = {}
        for label in self.__node__.labels:
            if label != self.__class__.__name__:
                labels[str(label).lower()] = True
        props_names = self.get_properties().keys()
        all_labels = [label for label in dir(self) if label not in props_names
                      and isinstance(getattr(self, label), bool)]
        for label in all_labels:
            if not labels.get(str(label).lower(), None):
                labels[str(label).lower()] = False
        return labels

    def set_properties(self, res):
        """
        Sets the properies of a node
        :param res: the map of properties and their values
        """
        for key, value in res.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError("Object %s does not have a %s attribute" %
                                 (self.ID, key))


    def get_relationships(self, direction):
        """
        Gets all the relationships of node
        :param direction: the direction of the relationship (INCOMING or
                          OUTGOING)
        :return: the list of relations
        """
        res = []
        for key in dir(self):
            value = getattr(self, key)
            if isinstance(value, RelatedObjects):
                r_type = value._RelatedObjects__match_args['r_type']
                if direction == RelatedTo and value._RelatedObjects__end_node:
                    for node_link in list(value):
                        res.append(LbRelationCacheObject(self, node_link,
                                                         hash(value), r_type))
                if direction == RelatedFrom and \
                        value._RelatedObjects__start_node:
                    for node_link in list(value):
                        res.append(LbRelationCacheObject(node_link, self,
                                                         hash(value), r_type))
        return res

    def __str__(self):
        return self.name


class Project(LbBaseGraphObject):
    """Object class for a project ex: BRUNEL, DAVINCI, etc"""
    __primarykey__ = "name"

    application = Label(name="Application")

    name = CaseInsensitiveProperty()
    sourceuri = Property()
    project = RelatedTo("ProjectVersion")
    pattern = RelatedTo("ProjectVersion")
    pkgproject = RelatedFrom("Datapkg", 'PKGPROJECT')

    def __init__(self, name, sourceuri=None):
        self.name = name
        self.sourceuri = sourceuri


class ProjectVersion(LbBaseGraphObject):
    """Object class for a version of a project. Related to Project object"""
    __primarykey__ = "name"

    toRelease = Label(name="ToRelease")
    patternVersion = Label(name="PatternVersion")
    active = Label(name="Active")
    used = Label(name="Used")

    name = Property()
    project_name = CaseInsensitiveProperty()
    version = Property()
    sourceuri = Property()
    Rev = Property()
    buildTool = Property()
    buildToolDate = Property()
    releasedDate = Property()
    commitID = Property()  # By default the value is set to None
    tags = Property()
    project = RelatedFrom("Project", 'PROJECT')
    pattern = RelatedFrom("Project", 'PATTERN')

    platform = RelatedTo("Platform")
    requested_platform = RelatedTo("Platform")
    requires = RelatedTo("ProjectVersion", 'REQUIRES')
    requiresFrom = RelatedFrom("ProjectVersion", 'REQUIRES')
    requiresPattern = RelatedTo("ProjectVersion", 'REQUIRES_PATTERN')
    requiresPatternFrom = RelatedFrom("ProjectVersion", 'REQUIRES_PATTERN')

    def __init__(self, project, version, commitID=None):
        self.project_name = project
        self.version = str(version)
        if commitID:
            self.commitID = commitID
        self.name = "%s_%s" % (self.project_name, self.version)


class Platform(LbBaseGraphObject):
    """Object class for a platform of a project."""
    __primarykey__ = "name"

    name = Property()
    platform = RelatedFrom("ProjectVersion", 'PLATFORM')
    requested_platform = RelatedFrom("ProjectVersion", 'REQUESTED_PLATFORM')

    def __init__(self, platform):
        self.name = platform


class Datapkg(LbBaseGraphObject):
    """Object class for a datapackages."""

    __primarykey__ = "name"

    name = CaseInsensitiveProperty()
    hat = Property()
    realname = Property()

    def __init__(self, name, hat, realname):
        self.name = name
        self.hat = str(hat)
        self.realname = str(realname)

    pkgproject = RelatedTo("Project")
    datapkg = RelatedTo("DatapkgVersion")


class DatapkgVersion(LbBaseGraphObject):
    """Object class for a version of a datapackages. Related to
    datapackages object"""

    __primarykey__ = "name"

    name = Property()
    datapkg_name = CaseInsensitiveProperty()
    version = Property()

    def __init__(self, datapkg, version):
        self.datapkg_name = datapkg
        self.version = str(version)
        self.name = "%s_%s" % (self.datapkg_name, self.version)

    datapkg = RelatedFrom("Datapkg", 'DATAPKG')
