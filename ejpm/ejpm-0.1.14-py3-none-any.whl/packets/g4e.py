"""
This file provides information of how to build and configure Geant4 framework:
https://gitlab.com/jlab-eic/g4e.git


"""

import os

from ejpm.engine.commands import run, workdir
from ejpm.engine.env_gen import Set, Prepend
from ejpm.engine.recipe import Recipe


class GeantInstallation(Recipe):
    """Provides data for building and installing Geant4 framework
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """


    def __init__(self):
        """
        Installs Genfit track fitting framework
        """

        # Set initial values for parent class and self
        super(GeantInstallation, self).__init__('g4e')
        self.clone_command = ''             # is set during self.setup(...)
        self.build_cmd = ''                 # is set during self.setup(...)
        self.config['branch'] = 'master'
        self.required_deps = ['clhep', 'root', 'hepmc', 'geant', 'vgm']

    def setup(self):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # use_common_dirs_scheme sets standard package variables:
        # source_path  = {app_path} / src   / {branch}       # Where the sources for the current version are located
        # build_path   = {app_path} / build / {branch}       # Where sources are built. Kind of temporary dir
        # install_path = {app_path} / geant-{branch}         # Where the binary installation is
        self.use_common_dirs_scheme()

        #
        # Git download link. Clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} https://gitlab.com/jlab-eic/g4e.git {source_path}"\
            .format(**self.config)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} -DCMAKE_CXX_STANDARD={cxx_standard} {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
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

        # Create build directory
        run('mkdir -p {}'.format(self.build_path))

        # go to our build directory
        workdir(self.build_path)

        # run scons && scons install
        run(self.build_cmd)

    def step_reinstall(self):
        """Delete everything and start over"""

        # clear sources directories if needed
        run('rm -rf {}'.format(self.app_path))

        # Now run build root
        self.step_install()

    @staticmethod
    def gen_env(data):
        """Generates environments to be set"""

        bin_path = os.path.join(data['install_path'], 'bin')
        yield Prepend('PATH', bin_path)  # to make available clhep-config and others
        yield Set('G4E_HOME', bin_path)
        yield Set('G4E_RESOURCES', bin_path + '/work')


    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "",
            'centos': ""
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }