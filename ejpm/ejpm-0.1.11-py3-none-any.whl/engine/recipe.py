# This module contains classes, which hold information about how to install packets
import os


class Recipe(object):
    """
    This class stores information which is pretty similar for each package (like directory structure)

    The important here is that while we try to stick to this naming, each package can override them if needed

    Usually this class is used like:

    # packets/my_packet.py file:

    MyPacketInstallationInstruction(PacketInstallationInstruction):
        # ... define your packet installation instruction by
        # defining:

        def set_app_path(...)  # - function that setups variables when the installation path is known

        # and logic with
        def step_install(...)  # - installs application
        def step_download(...) # - downloads from network
        def step...

    # usage of MyPacketInstallationInstruction is like:

    """

    def __init__(self, name):
        #
        # Short lowercase name of a packet
        self.name = name

        #
        # Next variables are set by ancestors
        self.config = {
            "app_name": self.name,
            "app_path"      : "",   # installation path of this packet, all other pathes relative to this
            "download_path" : "",   # where we download the source or clone git
            "source_path"   : "",   # The directory with source files for current version
            "build_path"    : "",   # The directory for cmake/scons build
            "install_path"  : "",   # The directory, where binary is installed
            "required_deps" : [],   # Packets which are required for this to run
            "optional_deps" : [],   # Optional packets
        }

    def setup(self):
        """This function is used to format and fill variables, when app_path is known download command"""
        # ... (!) inherited classes should implement its logic here
        raise NotImplementedError()

    def use_common_dirs_scheme(self):
        """Function sets common directory scheme. It is the same for many packets:
        """

        # where we download the source or clone git
        self.config["download_path"] = "{app_path}/src".format(app_path=self.app_path)

        # The directory with source files for current version
        self.config["source_path"] = "{app_path}/src/{branch}".format(**self.config)

        # The directory for cmake build
        self.config["build_path"] = "{app_path}/build/{branch}".format(**self.config)

        # The directory, where binary is installed
        self.config["install_path"] = "{app_path}/{app_name}-{branch}".format(**self.config)

    def step_install(self):
        """Installs application"""
        raise NotImplementedError()

    @property
    def app_path(self):
        return self.config["app_path"]

    @property
    def download_path(self):
        return self.config["download_path"]

    @property
    def source_path(self):
        return self.config["source_path"]

    @property
    def build_path(self):
        return self.config["build_path"]

    @property
    def install_path(self):
        return self.config["install_path"]

    @property
    def required_deps(self):
        return self.config["required_deps"]

    @required_deps.setter
    def required_deps(self, value):
        self.config["required_deps"] = value

    @property
    def optional_deps(self):
        return self.config["optional_deps"]

    @optional_deps.setter
    def optional_deps(self, value):
        self.config["optional_deps"] = value

    def source_dir_is_not_empty(self):
        return os.path.exists(self.source_path) \
               and os.path.isdir(self.source_path) \
               and os.listdir(self.source_path)
