"""
This file provides information of how to build and configure JANA2 packet:
https://github.com/JeffersonLab/JANA2

"""

import os

from ejpm.engine.commands import run, workdir, env
from ejpm.engine.env_gen import Prepend, Set, Append
from ejpm.engine.recipe import Recipe


class JanaInstallation(Recipe):
    """Provides data for building and installing JANA2 framework

    PacketInstallationInstruction is located in recipe.py and contains the next standard package variables:


    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """

    class DefaultConfig(object):
        download_path = ""     # where we download the source or clone git
        source_path = ""       # The directory with source files for current version
        build_path = ""        # The directory for cmake/scons build
        install_path = ""      # The directory, where binary is installed
        required_deps = []     # Packets which are required for this to run
        optional_deps = []     # Optional packets

    def __init__(self):
        super(JanaInstallation, self).__init__('jana')
        self.clone_command = ""
        self.build_command = ""
        self.config['branch'] = 'master'

    def setup(self):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme()

        #
        # Git download link. Clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} https://github.com/JeffersonLab/JANA2.git {source_path}"\
            .format(**self.config)

        #
        # scons installation command:
        self.build_command = "python2 {source_path}/scons/scons.py install -j{build_threads} PREFIX={install_path}"\
                             .format(**self.config)

    def step_install(self):
        self.step_clone()
        self.step_build()

    def step_clone(self):
        """Clones JANA from github mirror"""

        # Check the directory exists and not empty
        if os.path.exists(self.source_path) and os.path.isdir(self.source_path) and os.listdir(self.source_path):
            # The directory exists and is not empty. Nothing to do
            return
        else:
            # Create the directory
            run('mkdir -p {}'.format(self.source_path))

        # Execute git clone command
        run(self.clone_command)

    def step_build(self):
        """Builds JANA from the ground"""

        # # We use scons that is shipped with JANA2, for this we have to append PYTHONPATH
        # scons_dir = os.path.join(self.config['source_path'], 'scons')
        # old_pythonpath = os.environ.get('PYTHONPATH')
        #
        # if old_pythonpath:
        #     new_pythonpath = '{scons_dir};{old_pythonpath}'.format(scons_dir=scons_dir, old_pythonpath=old_pythonpath)
        # else:
        #     new_pythonpath = scons_dir
        #
        # env('PYTHONPATH', new_pythonpath)

        # Create build directory
        run('mkdir -p {}'.format(self.build_path))

        # go to source directory to invoke scons
        workdir(self.source_path)

        # run scons && scons install
        run(self.build_command)

    def step_reinstall(self):
        """Delete everything and start over"""

        # clear sources directories if needed
        run('rm -rf {}'.format(self.app_path))

        # Now run build root
        self.step_install()


    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""

        install_path = data['install_path']

        yield Set('JANA_HOME', install_path)
        yield Append('JANA_PLUGIN_PATH', '$JANA_HOME/plugins')
        yield Prepend('PATH', '$JANA_HOME/bin')

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "scons libxerces-c-dev curl python3-dev",
            'centos': "scons xerces curl"
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }
