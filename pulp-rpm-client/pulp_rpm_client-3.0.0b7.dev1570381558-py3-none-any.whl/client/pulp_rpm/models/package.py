# coding: utf-8

"""
    Pulp 3 API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)  # noqa: E501

    The version of the OpenAPI document: v3
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class Package(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'href': 'str',
        'created': 'datetime',
        'type': 'str',
        'artifact': 'str',
        'relative_path': 'str',
        'file': 'str',
        'repository': 'str',
        'name': 'str',
        'epoch': 'str',
        'version': 'str',
        'release': 'str',
        'arch': 'str',
        'pkg_id': 'str',
        'checksum_type': 'str',
        'summary': 'str',
        'description': 'str',
        'url': 'str',
        'changelogs': 'object',
        'files': 'object',
        'requires': 'object',
        'provides': 'object',
        'conflicts': 'object',
        'obsoletes': 'object',
        'suggests': 'object',
        'enhances': 'object',
        'recommends': 'object',
        'supplements': 'object',
        'location_base': 'str',
        'location_href': 'str',
        'rpm_buildhost': 'str',
        'rpm_group': 'str',
        'rpm_license': 'str',
        'rpm_packager': 'str',
        'rpm_sourcerpm': 'str',
        'rpm_vendor': 'str',
        'rpm_header_start': 'int',
        'rpm_header_end': 'int',
        'is_modular': 'bool',
        'size_archive': 'int',
        'size_installed': 'int',
        'size_package': 'int',
        'time_build': 'int',
        'time_file': 'int'
    }

    attribute_map = {
        'href': '_href',
        'created': '_created',
        'type': '_type',
        'artifact': 'artifact',
        'relative_path': 'relative_path',
        'file': 'file',
        'repository': 'repository',
        'name': 'name',
        'epoch': 'epoch',
        'version': 'version',
        'release': 'release',
        'arch': 'arch',
        'pkg_id': 'pkgId',
        'checksum_type': 'checksum_type',
        'summary': 'summary',
        'description': 'description',
        'url': 'url',
        'changelogs': 'changelogs',
        'files': 'files',
        'requires': 'requires',
        'provides': 'provides',
        'conflicts': 'conflicts',
        'obsoletes': 'obsoletes',
        'suggests': 'suggests',
        'enhances': 'enhances',
        'recommends': 'recommends',
        'supplements': 'supplements',
        'location_base': 'location_base',
        'location_href': 'location_href',
        'rpm_buildhost': 'rpm_buildhost',
        'rpm_group': 'rpm_group',
        'rpm_license': 'rpm_license',
        'rpm_packager': 'rpm_packager',
        'rpm_sourcerpm': 'rpm_sourcerpm',
        'rpm_vendor': 'rpm_vendor',
        'rpm_header_start': 'rpm_header_start',
        'rpm_header_end': 'rpm_header_end',
        'is_modular': 'is_modular',
        'size_archive': 'size_archive',
        'size_installed': 'size_installed',
        'size_package': 'size_package',
        'time_build': 'time_build',
        'time_file': 'time_file'
    }

    def __init__(self, href=None, created=None, type=None, artifact=None, relative_path=None, file=None, repository=None, name=None, epoch=None, version=None, release=None, arch=None, pkg_id=None, checksum_type=None, summary=None, description=None, url=None, changelogs=None, files=None, requires=None, provides=None, conflicts=None, obsoletes=None, suggests=None, enhances=None, recommends=None, supplements=None, location_base=None, location_href=None, rpm_buildhost=None, rpm_group=None, rpm_license=None, rpm_packager=None, rpm_sourcerpm=None, rpm_vendor=None, rpm_header_start=None, rpm_header_end=None, is_modular=None, size_archive=None, size_installed=None, size_package=None, time_build=None, time_file=None):  # noqa: E501
        """Package - a model defined in OpenAPI"""  # noqa: E501

        self._href = None
        self._created = None
        self._type = None
        self._artifact = None
        self._relative_path = None
        self._file = None
        self._repository = None
        self._name = None
        self._epoch = None
        self._version = None
        self._release = None
        self._arch = None
        self._pkg_id = None
        self._checksum_type = None
        self._summary = None
        self._description = None
        self._url = None
        self._changelogs = None
        self._files = None
        self._requires = None
        self._provides = None
        self._conflicts = None
        self._obsoletes = None
        self._suggests = None
        self._enhances = None
        self._recommends = None
        self._supplements = None
        self._location_base = None
        self._location_href = None
        self._rpm_buildhost = None
        self._rpm_group = None
        self._rpm_license = None
        self._rpm_packager = None
        self._rpm_sourcerpm = None
        self._rpm_vendor = None
        self._rpm_header_start = None
        self._rpm_header_end = None
        self._is_modular = None
        self._size_archive = None
        self._size_installed = None
        self._size_package = None
        self._time_build = None
        self._time_file = None
        self.discriminator = None

        if href is not None:
            self.href = href
        if created is not None:
            self.created = created
        if type is not None:
            self.type = type
        if artifact is not None:
            self.artifact = artifact
        self.relative_path = relative_path
        if file is not None:
            self.file = file
        if repository is not None:
            self.repository = repository
        if name is not None:
            self.name = name
        if epoch is not None:
            self.epoch = epoch
        if version is not None:
            self.version = version
        if release is not None:
            self.release = release
        if arch is not None:
            self.arch = arch
        if pkg_id is not None:
            self.pkg_id = pkg_id
        if checksum_type is not None:
            self.checksum_type = checksum_type
        if summary is not None:
            self.summary = summary
        if description is not None:
            self.description = description
        if url is not None:
            self.url = url
        if changelogs is not None:
            self.changelogs = changelogs
        if files is not None:
            self.files = files
        if requires is not None:
            self.requires = requires
        if provides is not None:
            self.provides = provides
        if conflicts is not None:
            self.conflicts = conflicts
        if obsoletes is not None:
            self.obsoletes = obsoletes
        if suggests is not None:
            self.suggests = suggests
        if enhances is not None:
            self.enhances = enhances
        if recommends is not None:
            self.recommends = recommends
        if supplements is not None:
            self.supplements = supplements
        if location_base is not None:
            self.location_base = location_base
        if location_href is not None:
            self.location_href = location_href
        if rpm_buildhost is not None:
            self.rpm_buildhost = rpm_buildhost
        if rpm_group is not None:
            self.rpm_group = rpm_group
        if rpm_license is not None:
            self.rpm_license = rpm_license
        if rpm_packager is not None:
            self.rpm_packager = rpm_packager
        if rpm_sourcerpm is not None:
            self.rpm_sourcerpm = rpm_sourcerpm
        if rpm_vendor is not None:
            self.rpm_vendor = rpm_vendor
        if rpm_header_start is not None:
            self.rpm_header_start = rpm_header_start
        if rpm_header_end is not None:
            self.rpm_header_end = rpm_header_end
        if is_modular is not None:
            self.is_modular = is_modular
        if size_archive is not None:
            self.size_archive = size_archive
        if size_installed is not None:
            self.size_installed = size_installed
        if size_package is not None:
            self.size_package = size_package
        if time_build is not None:
            self.time_build = time_build
        if time_file is not None:
            self.time_file = time_file

    @property
    def href(self):
        """Gets the href of this Package.  # noqa: E501


        :return: The href of this Package.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this Package.


        :param href: The href of this Package.  # noqa: E501
        :type: str
        """

        self._href = href

    @property
    def created(self):
        """Gets the created of this Package.  # noqa: E501

        Timestamp of creation.  # noqa: E501

        :return: The created of this Package.  # noqa: E501
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this Package.

        Timestamp of creation.  # noqa: E501

        :param created: The created of this Package.  # noqa: E501
        :type: datetime
        """

        self._created = created

    @property
    def type(self):
        """Gets the type of this Package.  # noqa: E501


        :return: The type of this Package.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this Package.


        :param type: The type of this Package.  # noqa: E501
        :type: str
        """
        if type is not None and len(type) < 1:
            raise ValueError("Invalid value for `type`, length must be greater than or equal to `1`")  # noqa: E501

        self._type = type

    @property
    def artifact(self):
        """Gets the artifact of this Package.  # noqa: E501

        Artifact file representing the physical content  # noqa: E501

        :return: The artifact of this Package.  # noqa: E501
        :rtype: str
        """
        return self._artifact

    @artifact.setter
    def artifact(self, artifact):
        """Sets the artifact of this Package.

        Artifact file representing the physical content  # noqa: E501

        :param artifact: The artifact of this Package.  # noqa: E501
        :type: str
        """

        self._artifact = artifact

    @property
    def relative_path(self):
        """Gets the relative_path of this Package.  # noqa: E501

        Path where the artifact is located relative to distributions base_path  # noqa: E501

        :return: The relative_path of this Package.  # noqa: E501
        :rtype: str
        """
        return self._relative_path

    @relative_path.setter
    def relative_path(self, relative_path):
        """Sets the relative_path of this Package.

        Path where the artifact is located relative to distributions base_path  # noqa: E501

        :param relative_path: The relative_path of this Package.  # noqa: E501
        :type: str
        """
        if relative_path is None:
            raise ValueError("Invalid value for `relative_path`, must not be `None`")  # noqa: E501
        if relative_path is not None and len(relative_path) < 1:
            raise ValueError("Invalid value for `relative_path`, length must be greater than or equal to `1`")  # noqa: E501

        self._relative_path = relative_path

    @property
    def file(self):
        """Gets the file of this Package.  # noqa: E501

        An uploaded file that should be turned into the artifact of the content unit.  # noqa: E501

        :return: The file of this Package.  # noqa: E501
        :rtype: str
        """
        return self._file

    @file.setter
    def file(self, file):
        """Sets the file of this Package.

        An uploaded file that should be turned into the artifact of the content unit.  # noqa: E501

        :param file: The file of this Package.  # noqa: E501
        :type: str
        """

        self._file = file

    @property
    def repository(self):
        """Gets the repository of this Package.  # noqa: E501

        A URI of a repository the new content unit should be associated with.  # noqa: E501

        :return: The repository of this Package.  # noqa: E501
        :rtype: str
        """
        return self._repository

    @repository.setter
    def repository(self, repository):
        """Sets the repository of this Package.

        A URI of a repository the new content unit should be associated with.  # noqa: E501

        :param repository: The repository of this Package.  # noqa: E501
        :type: str
        """

        self._repository = repository

    @property
    def name(self):
        """Gets the name of this Package.  # noqa: E501

        Name of the package  # noqa: E501

        :return: The name of this Package.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this Package.

        Name of the package  # noqa: E501

        :param name: The name of this Package.  # noqa: E501
        :type: str
        """
        if name is not None and len(name) < 1:
            raise ValueError("Invalid value for `name`, length must be greater than or equal to `1`")  # noqa: E501

        self._name = name

    @property
    def epoch(self):
        """Gets the epoch of this Package.  # noqa: E501

        The package's epoch  # noqa: E501

        :return: The epoch of this Package.  # noqa: E501
        :rtype: str
        """
        return self._epoch

    @epoch.setter
    def epoch(self, epoch):
        """Sets the epoch of this Package.

        The package's epoch  # noqa: E501

        :param epoch: The epoch of this Package.  # noqa: E501
        :type: str
        """

        self._epoch = epoch

    @property
    def version(self):
        """Gets the version of this Package.  # noqa: E501

        The version of the package. For example, '2.8.0'  # noqa: E501

        :return: The version of this Package.  # noqa: E501
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this Package.

        The version of the package. For example, '2.8.0'  # noqa: E501

        :param version: The version of this Package.  # noqa: E501
        :type: str
        """
        if version is not None and len(version) < 1:
            raise ValueError("Invalid value for `version`, length must be greater than or equal to `1`")  # noqa: E501

        self._version = version

    @property
    def release(self):
        """Gets the release of this Package.  # noqa: E501

        The release of a particular version of the package. e.g. '1.el7' or '3.f24'  # noqa: E501

        :return: The release of this Package.  # noqa: E501
        :rtype: str
        """
        return self._release

    @release.setter
    def release(self, release):
        """Sets the release of this Package.

        The release of a particular version of the package. e.g. '1.el7' or '3.f24'  # noqa: E501

        :param release: The release of this Package.  # noqa: E501
        :type: str
        """
        if release is not None and len(release) < 1:
            raise ValueError("Invalid value for `release`, length must be greater than or equal to `1`")  # noqa: E501

        self._release = release

    @property
    def arch(self):
        """Gets the arch of this Package.  # noqa: E501

        The target architecture for a package.For example, 'x86_64', 'i686', or 'noarch'  # noqa: E501

        :return: The arch of this Package.  # noqa: E501
        :rtype: str
        """
        return self._arch

    @arch.setter
    def arch(self, arch):
        """Sets the arch of this Package.

        The target architecture for a package.For example, 'x86_64', 'i686', or 'noarch'  # noqa: E501

        :param arch: The arch of this Package.  # noqa: E501
        :type: str
        """
        if arch is not None and len(arch) < 1:
            raise ValueError("Invalid value for `arch`, length must be greater than or equal to `1`")  # noqa: E501

        self._arch = arch

    @property
    def pkg_id(self):
        """Gets the pkg_id of this Package.  # noqa: E501

        Checksum of the package file  # noqa: E501

        :return: The pkg_id of this Package.  # noqa: E501
        :rtype: str
        """
        return self._pkg_id

    @pkg_id.setter
    def pkg_id(self, pkg_id):
        """Sets the pkg_id of this Package.

        Checksum of the package file  # noqa: E501

        :param pkg_id: The pkg_id of this Package.  # noqa: E501
        :type: str
        """
        if pkg_id is not None and len(pkg_id) < 1:
            raise ValueError("Invalid value for `pkg_id`, length must be greater than or equal to `1`")  # noqa: E501

        self._pkg_id = pkg_id

    @property
    def checksum_type(self):
        """Gets the checksum_type of this Package.  # noqa: E501

        Type of checksum, e.g. 'sha256', 'md5'  # noqa: E501

        :return: The checksum_type of this Package.  # noqa: E501
        :rtype: str
        """
        return self._checksum_type

    @checksum_type.setter
    def checksum_type(self, checksum_type):
        """Sets the checksum_type of this Package.

        Type of checksum, e.g. 'sha256', 'md5'  # noqa: E501

        :param checksum_type: The checksum_type of this Package.  # noqa: E501
        :type: str
        """
        if checksum_type is not None and len(checksum_type) < 1:
            raise ValueError("Invalid value for `checksum_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._checksum_type = checksum_type

    @property
    def summary(self):
        """Gets the summary of this Package.  # noqa: E501

        Short description of the packaged software  # noqa: E501

        :return: The summary of this Package.  # noqa: E501
        :rtype: str
        """
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Sets the summary of this Package.

        Short description of the packaged software  # noqa: E501

        :param summary: The summary of this Package.  # noqa: E501
        :type: str
        """

        self._summary = summary

    @property
    def description(self):
        """Gets the description of this Package.  # noqa: E501

        In-depth description of the packaged software  # noqa: E501

        :return: The description of this Package.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Package.

        In-depth description of the packaged software  # noqa: E501

        :param description: The description of this Package.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def url(self):
        """Gets the url of this Package.  # noqa: E501

        URL with more information about the packaged software  # noqa: E501

        :return: The url of this Package.  # noqa: E501
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """Sets the url of this Package.

        URL with more information about the packaged software  # noqa: E501

        :param url: The url of this Package.  # noqa: E501
        :type: str
        """

        self._url = url

    @property
    def changelogs(self):
        """Gets the changelogs of this Package.  # noqa: E501

        Changelogs that package contains  # noqa: E501

        :return: The changelogs of this Package.  # noqa: E501
        :rtype: object
        """
        return self._changelogs

    @changelogs.setter
    def changelogs(self, changelogs):
        """Sets the changelogs of this Package.

        Changelogs that package contains  # noqa: E501

        :param changelogs: The changelogs of this Package.  # noqa: E501
        :type: object
        """

        self._changelogs = changelogs

    @property
    def files(self):
        """Gets the files of this Package.  # noqa: E501

        Files that package contains  # noqa: E501

        :return: The files of this Package.  # noqa: E501
        :rtype: object
        """
        return self._files

    @files.setter
    def files(self, files):
        """Sets the files of this Package.

        Files that package contains  # noqa: E501

        :param files: The files of this Package.  # noqa: E501
        :type: object
        """

        self._files = files

    @property
    def requires(self):
        """Gets the requires of this Package.  # noqa: E501

        Capabilities the package requires  # noqa: E501

        :return: The requires of this Package.  # noqa: E501
        :rtype: object
        """
        return self._requires

    @requires.setter
    def requires(self, requires):
        """Sets the requires of this Package.

        Capabilities the package requires  # noqa: E501

        :param requires: The requires of this Package.  # noqa: E501
        :type: object
        """

        self._requires = requires

    @property
    def provides(self):
        """Gets the provides of this Package.  # noqa: E501

        Capabilities the package provides  # noqa: E501

        :return: The provides of this Package.  # noqa: E501
        :rtype: object
        """
        return self._provides

    @provides.setter
    def provides(self, provides):
        """Sets the provides of this Package.

        Capabilities the package provides  # noqa: E501

        :param provides: The provides of this Package.  # noqa: E501
        :type: object
        """

        self._provides = provides

    @property
    def conflicts(self):
        """Gets the conflicts of this Package.  # noqa: E501

        Capabilities the package conflicts  # noqa: E501

        :return: The conflicts of this Package.  # noqa: E501
        :rtype: object
        """
        return self._conflicts

    @conflicts.setter
    def conflicts(self, conflicts):
        """Sets the conflicts of this Package.

        Capabilities the package conflicts  # noqa: E501

        :param conflicts: The conflicts of this Package.  # noqa: E501
        :type: object
        """

        self._conflicts = conflicts

    @property
    def obsoletes(self):
        """Gets the obsoletes of this Package.  # noqa: E501

        Capabilities the package obsoletes  # noqa: E501

        :return: The obsoletes of this Package.  # noqa: E501
        :rtype: object
        """
        return self._obsoletes

    @obsoletes.setter
    def obsoletes(self, obsoletes):
        """Sets the obsoletes of this Package.

        Capabilities the package obsoletes  # noqa: E501

        :param obsoletes: The obsoletes of this Package.  # noqa: E501
        :type: object
        """

        self._obsoletes = obsoletes

    @property
    def suggests(self):
        """Gets the suggests of this Package.  # noqa: E501

        Capabilities the package suggests  # noqa: E501

        :return: The suggests of this Package.  # noqa: E501
        :rtype: object
        """
        return self._suggests

    @suggests.setter
    def suggests(self, suggests):
        """Sets the suggests of this Package.

        Capabilities the package suggests  # noqa: E501

        :param suggests: The suggests of this Package.  # noqa: E501
        :type: object
        """

        self._suggests = suggests

    @property
    def enhances(self):
        """Gets the enhances of this Package.  # noqa: E501

        Capabilities the package enhances  # noqa: E501

        :return: The enhances of this Package.  # noqa: E501
        :rtype: object
        """
        return self._enhances

    @enhances.setter
    def enhances(self, enhances):
        """Sets the enhances of this Package.

        Capabilities the package enhances  # noqa: E501

        :param enhances: The enhances of this Package.  # noqa: E501
        :type: object
        """

        self._enhances = enhances

    @property
    def recommends(self):
        """Gets the recommends of this Package.  # noqa: E501

        Capabilities the package recommends  # noqa: E501

        :return: The recommends of this Package.  # noqa: E501
        :rtype: object
        """
        return self._recommends

    @recommends.setter
    def recommends(self, recommends):
        """Sets the recommends of this Package.

        Capabilities the package recommends  # noqa: E501

        :param recommends: The recommends of this Package.  # noqa: E501
        :type: object
        """

        self._recommends = recommends

    @property
    def supplements(self):
        """Gets the supplements of this Package.  # noqa: E501

        Capabilities the package supplements  # noqa: E501

        :return: The supplements of this Package.  # noqa: E501
        :rtype: object
        """
        return self._supplements

    @supplements.setter
    def supplements(self, supplements):
        """Sets the supplements of this Package.

        Capabilities the package supplements  # noqa: E501

        :param supplements: The supplements of this Package.  # noqa: E501
        :type: object
        """

        self._supplements = supplements

    @property
    def location_base(self):
        """Gets the location_base of this Package.  # noqa: E501

        Base location of this package  # noqa: E501

        :return: The location_base of this Package.  # noqa: E501
        :rtype: str
        """
        return self._location_base

    @location_base.setter
    def location_base(self, location_base):
        """Sets the location_base of this Package.

        Base location of this package  # noqa: E501

        :param location_base: The location_base of this Package.  # noqa: E501
        :type: str
        """

        self._location_base = location_base

    @property
    def location_href(self):
        """Gets the location_href of this Package.  # noqa: E501

        Relative location of package to the repodata  # noqa: E501

        :return: The location_href of this Package.  # noqa: E501
        :rtype: str
        """
        return self._location_href

    @location_href.setter
    def location_href(self, location_href):
        """Sets the location_href of this Package.

        Relative location of package to the repodata  # noqa: E501

        :param location_href: The location_href of this Package.  # noqa: E501
        :type: str
        """
        if location_href is not None and len(location_href) < 1:
            raise ValueError("Invalid value for `location_href`, length must be greater than or equal to `1`")  # noqa: E501

        self._location_href = location_href

    @property
    def rpm_buildhost(self):
        """Gets the rpm_buildhost of this Package.  # noqa: E501

        Hostname of the system that built the package  # noqa: E501

        :return: The rpm_buildhost of this Package.  # noqa: E501
        :rtype: str
        """
        return self._rpm_buildhost

    @rpm_buildhost.setter
    def rpm_buildhost(self, rpm_buildhost):
        """Sets the rpm_buildhost of this Package.

        Hostname of the system that built the package  # noqa: E501

        :param rpm_buildhost: The rpm_buildhost of this Package.  # noqa: E501
        :type: str
        """

        self._rpm_buildhost = rpm_buildhost

    @property
    def rpm_group(self):
        """Gets the rpm_group of this Package.  # noqa: E501

        RPM group (See: http://fedoraproject.org/wiki/RPMGroups)  # noqa: E501

        :return: The rpm_group of this Package.  # noqa: E501
        :rtype: str
        """
        return self._rpm_group

    @rpm_group.setter
    def rpm_group(self, rpm_group):
        """Sets the rpm_group of this Package.

        RPM group (See: http://fedoraproject.org/wiki/RPMGroups)  # noqa: E501

        :param rpm_group: The rpm_group of this Package.  # noqa: E501
        :type: str
        """

        self._rpm_group = rpm_group

    @property
    def rpm_license(self):
        """Gets the rpm_license of this Package.  # noqa: E501

        License term applicable to the package software (GPLv2, etc.)  # noqa: E501

        :return: The rpm_license of this Package.  # noqa: E501
        :rtype: str
        """
        return self._rpm_license

    @rpm_license.setter
    def rpm_license(self, rpm_license):
        """Sets the rpm_license of this Package.

        License term applicable to the package software (GPLv2, etc.)  # noqa: E501

        :param rpm_license: The rpm_license of this Package.  # noqa: E501
        :type: str
        """

        self._rpm_license = rpm_license

    @property
    def rpm_packager(self):
        """Gets the rpm_packager of this Package.  # noqa: E501

        Person or persons responsible for creating the package  # noqa: E501

        :return: The rpm_packager of this Package.  # noqa: E501
        :rtype: str
        """
        return self._rpm_packager

    @rpm_packager.setter
    def rpm_packager(self, rpm_packager):
        """Sets the rpm_packager of this Package.

        Person or persons responsible for creating the package  # noqa: E501

        :param rpm_packager: The rpm_packager of this Package.  # noqa: E501
        :type: str
        """

        self._rpm_packager = rpm_packager

    @property
    def rpm_sourcerpm(self):
        """Gets the rpm_sourcerpm of this Package.  # noqa: E501

        Name of the source package (srpm) the package was built from  # noqa: E501

        :return: The rpm_sourcerpm of this Package.  # noqa: E501
        :rtype: str
        """
        return self._rpm_sourcerpm

    @rpm_sourcerpm.setter
    def rpm_sourcerpm(self, rpm_sourcerpm):
        """Sets the rpm_sourcerpm of this Package.

        Name of the source package (srpm) the package was built from  # noqa: E501

        :param rpm_sourcerpm: The rpm_sourcerpm of this Package.  # noqa: E501
        :type: str
        """

        self._rpm_sourcerpm = rpm_sourcerpm

    @property
    def rpm_vendor(self):
        """Gets the rpm_vendor of this Package.  # noqa: E501

        Name of the organization that produced the package  # noqa: E501

        :return: The rpm_vendor of this Package.  # noqa: E501
        :rtype: str
        """
        return self._rpm_vendor

    @rpm_vendor.setter
    def rpm_vendor(self, rpm_vendor):
        """Sets the rpm_vendor of this Package.

        Name of the organization that produced the package  # noqa: E501

        :param rpm_vendor: The rpm_vendor of this Package.  # noqa: E501
        :type: str
        """

        self._rpm_vendor = rpm_vendor

    @property
    def rpm_header_start(self):
        """Gets the rpm_header_start of this Package.  # noqa: E501

        First byte of the header  # noqa: E501

        :return: The rpm_header_start of this Package.  # noqa: E501
        :rtype: int
        """
        return self._rpm_header_start

    @rpm_header_start.setter
    def rpm_header_start(self, rpm_header_start):
        """Sets the rpm_header_start of this Package.

        First byte of the header  # noqa: E501

        :param rpm_header_start: The rpm_header_start of this Package.  # noqa: E501
        :type: int
        """

        self._rpm_header_start = rpm_header_start

    @property
    def rpm_header_end(self):
        """Gets the rpm_header_end of this Package.  # noqa: E501

        Last byte of the header  # noqa: E501

        :return: The rpm_header_end of this Package.  # noqa: E501
        :rtype: int
        """
        return self._rpm_header_end

    @rpm_header_end.setter
    def rpm_header_end(self, rpm_header_end):
        """Sets the rpm_header_end of this Package.

        Last byte of the header  # noqa: E501

        :param rpm_header_end: The rpm_header_end of this Package.  # noqa: E501
        :type: int
        """

        self._rpm_header_end = rpm_header_end

    @property
    def is_modular(self):
        """Gets the is_modular of this Package.  # noqa: E501

        Flag to identify if the package is modular  # noqa: E501

        :return: The is_modular of this Package.  # noqa: E501
        :rtype: bool
        """
        return self._is_modular

    @is_modular.setter
    def is_modular(self, is_modular):
        """Sets the is_modular of this Package.

        Flag to identify if the package is modular  # noqa: E501

        :param is_modular: The is_modular of this Package.  # noqa: E501
        :type: bool
        """

        self._is_modular = is_modular

    @property
    def size_archive(self):
        """Gets the size_archive of this Package.  # noqa: E501

        Size, in bytes, of the archive portion of the original package file  # noqa: E501

        :return: The size_archive of this Package.  # noqa: E501
        :rtype: int
        """
        return self._size_archive

    @size_archive.setter
    def size_archive(self, size_archive):
        """Sets the size_archive of this Package.

        Size, in bytes, of the archive portion of the original package file  # noqa: E501

        :param size_archive: The size_archive of this Package.  # noqa: E501
        :type: int
        """

        self._size_archive = size_archive

    @property
    def size_installed(self):
        """Gets the size_installed of this Package.  # noqa: E501

        Total size, in bytes, of every file installed by this package  # noqa: E501

        :return: The size_installed of this Package.  # noqa: E501
        :rtype: int
        """
        return self._size_installed

    @size_installed.setter
    def size_installed(self, size_installed):
        """Sets the size_installed of this Package.

        Total size, in bytes, of every file installed by this package  # noqa: E501

        :param size_installed: The size_installed of this Package.  # noqa: E501
        :type: int
        """

        self._size_installed = size_installed

    @property
    def size_package(self):
        """Gets the size_package of this Package.  # noqa: E501

        Size, in bytes, of the package  # noqa: E501

        :return: The size_package of this Package.  # noqa: E501
        :rtype: int
        """
        return self._size_package

    @size_package.setter
    def size_package(self, size_package):
        """Sets the size_package of this Package.

        Size, in bytes, of the package  # noqa: E501

        :param size_package: The size_package of this Package.  # noqa: E501
        :type: int
        """

        self._size_package = size_package

    @property
    def time_build(self):
        """Gets the time_build of this Package.  # noqa: E501

        Time the package was built in seconds since the epoch  # noqa: E501

        :return: The time_build of this Package.  # noqa: E501
        :rtype: int
        """
        return self._time_build

    @time_build.setter
    def time_build(self, time_build):
        """Sets the time_build of this Package.

        Time the package was built in seconds since the epoch  # noqa: E501

        :param time_build: The time_build of this Package.  # noqa: E501
        :type: int
        """

        self._time_build = time_build

    @property
    def time_file(self):
        """Gets the time_file of this Package.  # noqa: E501

        The 'file' time attribute in the primary XML - file mtime in seconds since the epoch.  # noqa: E501

        :return: The time_file of this Package.  # noqa: E501
        :rtype: int
        """
        return self._time_file

    @time_file.setter
    def time_file(self, time_file):
        """Sets the time_file of this Package.

        The 'file' time attribute in the primary XML - file mtime in seconds since the epoch.  # noqa: E501

        :param time_file: The time_file of this Package.  # noqa: E501
        :type: int
        """

        self._time_file = time_file

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, Package):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
