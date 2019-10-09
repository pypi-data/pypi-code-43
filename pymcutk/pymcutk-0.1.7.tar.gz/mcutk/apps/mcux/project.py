import os
import glob
import logging
import tempfile

from difflib import SequenceMatcher
from xml.etree import cElementTree as ET
from distutils.version import LooseVersion

from mcutk.apps import eclipse
from mcutk.apps.projectbase import ProjectBase
from mcutk.exceptions import ProjectNotFound, InvalidProject, ProjectParserError


class Project(eclipse.Project):
    """MCUXpresso SDK and projects parser tool."""

    PROJECT_EXTENSION = '.xml'


    @classmethod
    def frompath(cls, path):
        """Return a project instance from a given file path or directory.

        If path is a directory, it will search the project file and return an instance.
        Else this will raise mcutk.apps.exceptions.ProjectNotFound.
        """
        if not os.path.exists(path):
            raise ProjectNotFound("No such file or directory: %s", path)

        if os.path.isfile(path) and path.endswith(cls.PROJECT_EXTENSION):
            return cls(path)

        instance = None
        for file in glob.glob(path + "/.project"):
            with open(file) as f:
                content = f.read()
                if '<name>mcux</name>' in content or 'mcuxpresso' in content:
                    instance = cls(file)
                    break

        if instance:
            return instance

        for file in glob.glob(path + "/*" + cls.PROJECT_EXTENSION):
            try:
                instance = cls(file)
                break
            except InvalidProject:
                pass
        else:
            raise ProjectNotFound("Not found <example_app>.xml")

        return instance



    def __init__(self, prjpath, sdk_root=None, **kwargs):
        """MCUXPressoIDE project constructor.

        Arguments:
            prjpath {str} -- path to <name>.xml

        Keyword Arguments:
            sdk_root {str} -- path to sdk package root, default {None} that will be loaded from xml.
        """
        super(Project, self).__init__(prjpath, **kwargs)
        self._is_package = False
        self._sdk_root = sdk_root
        self._name = ''
        self._targets = None
        self._sdkmanifest = None
        self._example_id = None
        self._nature = 'org.eclipse.cdt.core.cnature'

        # eclipse project
        self._is_package = not (prjpath.endswith('.project') or prjpath.endswith('.cproject'))

        if self._is_package:
            self._load_from_sdk_package(prjpath)
            self._properties_init()
        else:
            self._load_from_eclipse_project(prjpath)



    @property
    def is_enabled(self):
        if not self.is_package:
            return True

        # check manifest: this exmaple is enabled for mcux
        example_info = self.sdkmanifest.find_example(self._example_id)

        # manifest version 3.1
        if self.sdkmanifest.manifest_version == "3.1":
            return True

        return "mcux" in example_info.get("toolchain", "")




    @property
    def sdkmanifest(self):
        return self._sdkmanifest



    @sdkmanifest.setter
    def sdkmanifest(self, value):
        if not isinstance(value, SDKManifest):
            raise ValueError("Must be a SDKManifest object")

        self._sdkmanifest = value





    @property
    def is_package(self):
        """Package project or standard eclipse project"""
        return self._is_package





    def _load_from_eclipse_project(self, path):
        """Load from Eclipse C/C++ project"""
        self.parse(path)




    def _load_from_sdk_package(self, path):
        """Load from SDK <app>.xml and *_manifest*.xml.
            1. Parse <app>.xml to get manifest.xml,
            2. Get related information from manifest.
        """

        self._targets = self._conf.keys()

        xmlroot = ET.parse(path).getroot()
        example_node = xmlroot.find('./example')
        if example_node is None:
            raise InvalidProject('Unable to find <example> node. %s'%path)

        self._example_id = example_node.attrib.get('id')
        # in some situation, the name attribute is not too simple
        # that is not full project name for mcux, we have to use a workaround
        # to get project name from path.
        # self._name = example_node.attrib.get('name')
        self._name = os.path.basename(path).replace('.xml', '')


        try:
            self._nature = example_node.find('projects/project[@nature]').attrib.get('nature')
        except:
            pass

        if not self._example_id:
            raise ProjectParserError('None id in exmaple node! %s'%self.prjpath)


        self._conf = {
            'Debug': self._example_id + '/Debug/',
            'Release': self._example_id + '/Release/'
        }


        if self.sdkmanifest:
            return


        # Automaticlly find and load SDKManifest
        prjdir_abs = os.path.abspath(self.prjdir).replace('\\', '/')

        def _search_node(node):
            """get sdk_root from an XML element node."""
            if node is None:
                return

            source_path = node.attrib.get('path')
            if not source_path:
                return

            if source_path in prjdir_abs:
                sdk_root = prjdir_abs.replace(source_path, "")
            else:
                match = SequenceMatcher(None, prjdir_abs, source_path).find_longest_match(0, len(prjdir_abs), 0, len(source_path))
                sdk_root = prjdir_abs[:match.a]

            if os.path.exists(sdk_root):
                return sdk_root
            return


        def _search_possible_nodes():
            possible_nodes = [
                './source[@type="src"]',
                './source'
            ]

            for p in possible_nodes:
                for node in example_node.findall(p):
                    sdk_root = _search_node(node)

                    if not sdk_root:
                        continue

                    try:
                        return SDKManifest.load_from_dir(sdk_root)
                        break
                    except ProjectParserError:
                        pass

        def _search_from_local():
            # In some situation, example.xml not include the source element.
            # Added a workaround to find mainfest file in it's parent.
            current_dir = prjdir_abs
            while True:
                parent_dir = os.path.dirname(current_dir)
                # system root
                if parent_dir == current_dir:
                    break
                try:
                    return SDKManifest.load_from_dir(parent_dir)
                except ProjectParserError:
                    pass

                current_dir = parent_dir


        manifest = _search_possible_nodes()

        if not manifest:
            manifest = _search_from_local()

        if manifest:
            self.sdkmanifest = manifest
        else:
            raise ProjectParserError("Unable to find SDK Manifest!")





    def _properties_init(self):
        """Init build properties variable.

        sdk.location = D:/Users/B46681/Desktop/SDK_2.0_MK64FN1M0xxx12-drop4
            This is the location where your SDK have been downloaded.
            You can use either zip or folder containing the SDK
            Please remember that if you want to create linked resources into your project(i.e. standalone = false) you need to use a folder instead of a zip.
            NOTE: on Windows you have to use "//" or "/".

        example.xml = D:/Users/B46681/Desktop/SDK_2.0_MK64FN1M0xxx12-drop4/boards/frdmk64f/demo_apps/hello_world/mcux/hello_world.xml
            If adding the "example.xml" property, the examples are retrieved from that specific file and shall valid against the used SDK
            NOTE: on Windows you have to use "//" or "/".

        nature = org.eclipse.cdt.core.cnature
            This represents the nature of your project (i.e. C or C++)
            It can be:
                - org.eclipse.cdt.core.cnature for C projects
                - org.eclipse.cdt.core.ccnature for C++ projects
                (Please remember that the example your're going to create shall support the C++ nature)

        standalone = true
            If true, it will copy the files from the SDK, otherwise it will link them.
            Note: linked resources will be only created if the SDK is provided as a folder

        project.build = true
            If true, the project will be compiled, otherwise the project is only created.

        clean.workspace = true
            True, if you want to clear the workspace used, false otherwise

        build.all = false
            If true, all the examples from all the SDK will be created, otherwise you need specify the SDK name

        skip.default = false
            If true, skip the default SDKPackages folder and all its content
            Default is false

        sdk.name = SDK_2.0_MK64FN1M0xxx12
            The SDK name (i.e. the folder/file name without extension)
            NOTE: only used when build.all = false

        board.id = frdmk64f
            The board id as for the manifest definition
            NOTE: only used when build.all = false

        Other Settings:
            verbose = true
                If true, more info will be provided using stdout

            indexer = false
                If true, enable the CDT indexer, false otherwise

            project.build.log = true
                If true, show the CDT build log, false otherwise

            simple.project.name = true

        """
        self._buildproperties = {
            'sdk.location': None,
            'example.xml': None,
            'nature': 'org.eclipse.cdt.core.cnature',
            'standalone': 'true',
            'project.build': 'true',
            'clean.workspace': 'true',
            'build.all': 'false',
            'build.config': 'debug',
            'simple.project.name': 'false',
            'use.other.files': 'true ',
            'skip.default': 'true',
            'sdk.name': None,
            'board.id': '',
            'verbose': 'false',
            'indexer': 'false',
            'use.io.console': 'false',
            'project.build.log': 'true'
        }


    def gen_properties(self, target, dir=None):
        """Return a file path for properties file.

        Arguments:
            target -- {string} target configuration
            dir -- {string} the location to place the new geneated file, default is system tempfile.

        """
        # boardid will effect workspace path
        board_ids = self.sdkmanifest.boards
        boardid = self._example_id.replace("_" + self._name, '')
        if boardid not in board_ids:
            boardid = board_ids[0]

        logging.info("SDK Manifest Version: %s", self.sdkmanifest.manifest_version)

        self.setproperties("example.xml", self.prjpath.replace('\\', '/'))
        self.setproperties("sdk.location", self.sdkmanifest.sdk_root.replace('\\', '/'))
        self.setproperties("nature", self.nature)
        self.setproperties("sdk.name", self.sdkmanifest.sdk_name)
        self.setproperties("board.id", boardid)
        self.setproperties("build.config", target)


        with tempfile.NamedTemporaryFile(dir=None, delete=False, prefix="mcuxpresso_", mode='w') as f:
            for per_property, value in self._buildproperties.items():
                f.writelines("{0} = {1}\r\n".format(per_property, value))
            properties_file = f.name

        logging.debug('properties file: %s', properties_file)
        return properties_file



    def setproperties(self, attrib, value):
        """ Set the value of self._buildproperties"""

        self._buildproperties[attrib] = value



    @property
    def nature(self):
        return self._nature



    @property
    def targets(self):
        """Return all targets name

        Returns:
            list -- a list of targets
        """
        if self._targets:
            return list(self._targets)
        else:
            return ['Debug', 'Release']


    @property
    def name(self):
        """Return the application name

        Returns:
            string --- app name
        """
        return self._name








class SDKManifest(object):
    """NXP MCUXpresso SDK Manifest Parser."""


    @classmethod
    def load_from_dir(cls, sdk_root):
        """Load latest version of manifest from directory."""

        manifestfilelist = glob.glob("{0}/*_manifest*.xml".format(sdk_root))
        if not manifestfilelist:
            raise ProjectParserError("cannot found manifest file")

        if len(manifestfilelist) == 1:
            return SDKManifest(manifestfilelist[0])

        # Find the max version
        file_versions = {}
        for per_file in manifestfilelist:
            version_str = per_file.replace('.xml', '').split('_manifest')[-1]
            version =  version_str[1:] if version_str.startswith('_') else version_str
            if version:
                file_versions[version] = per_file

        ver_latest = sorted(file_versions.keys(), key=lambda v: LooseVersion(v))[-1]
        manifest_path = file_versions[ver_latest].replace("\\",'/')

        return SDKManifest(manifest_path)




    def __init__(self, filepath):
        xmlParser = ET.parse(filepath)
        self._xmlroot = xmlParser.getroot()
        self._sdk_root = os.path.dirname(filepath)
        self._manifest_version = self._xmlroot.attrib['format_version']
        self._sdk_name = self._xmlroot.attrib["id"]
        self._sdk_version = self._xmlroot.find('./ksdk').attrib['version']

    @property
    def sdk_version(self):
        return self._sdk_version



    @property
    def sdk_name(self):
        return self._sdk_name



    @property
    def manifest_version(self):
        return self._manifest_version


    def find_example(self, example_id):
        """Return a dict which contain exmaple attributes.

        Keys:
            - id
            - name
            - toolchain
            - brief
            - category
            - path
        """
        xpath = './boards/board/examples/example[@id="{0}"]'.format(example_id)
        node = self._xmlroot.find(xpath)
        if not node:
            raise Exception("Cannot found example in manifest, id: %s", example_id)

        return node.attrib

    @property
    def boards(self):
        xpath = './boards/board'
        nodes = self._xmlroot.findall(xpath)
        return [n.attrib['id'] for n in nodes]



    @property
    def sdk_root(self):
        return self._sdk_root





