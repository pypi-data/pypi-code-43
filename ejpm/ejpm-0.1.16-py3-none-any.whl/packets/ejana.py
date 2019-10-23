"""
This file provides information of how to build and configure EIC Jana (ejana) framework:
https://gitlab.com/eic/ejana

"""

import os

from ejpm.engine.env_gen import Set, Prepend
from ejpm.engine.recipe import Recipe
from ejpm.engine.commands import run, env, workdir


class EjanaInstallation(Recipe):
    """Provides data for building and installing JANA framework

    PackageInstallationContext is located in recipe.py and contains the next standard package variables:

    version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
    glb_app_path = Context.work_dir                  # The directory where all other packets are installed
    source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
    build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
    install_path = {app_path}/root-{version}         # Where the binary installation is
    """


    def __init__(self):
        """
        """
        super(EjanaInstallation, self).__init__('ejana')
        self.clone_command = ""
        self.build_command = ""
        self.required_deps = ['clhep', 'root', 'rave', 'genfit', 'hepmc', 'eic-smear', 'jana']
        self.config['branch'] = 'master'
        self.config['install_mode'] = 'dev'

    def _setup_dev(self):
        """Sets all variables like source dirs, build dirs, etc"""

        # For dev version we don't use common path scheme
        self.config['build_threads'] = 1

        # The directory with source files for current version
        self.config['source_path'] = "{app_path}/dev".format(**self.config)
        self.config['build_path'] = "{app_path}/dev/cmake-build-debug".format(**self.config)  # build in dev directory
        self.config['install_path'] = "{app_path}/dev/compiled".format(**self.config)

        #
        # ejana download link
        self.clone_command = "git clone -b {branch} https://gitlab.com/eic/ejana.git {source_path}"\
                             .format(**self.config)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(**self.config)

    def setup(self):
        """Sets all variables like source dirs, build dirs, etc"""

        # (!) at this point we alwais use dev environment
        if self.config['install_mode'] == 'dev':
            return self._setup_dev()

        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme()

        #
        # Git download link. Clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} https://gitlab.com/eic/ejana.git {source_path}"\
            .format(**self.config)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(**self.config)  # make global options like '-j8'. Skip now

    def step_install(self):
        self.step_clone()
        self.step_build()

    def step_clone(self):
        """Clones JANA from github mirror"""

        # Check the directory exists and not empty
        if self.source_dir_is_not_empty():
            return  # The directory exists and is not empty. Nothing to do

        run('mkdir -p {source_path}'.format(**self.config))   # Create the directory
        run(self.clone_command)                               # Execute git clone command

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
        path = data['install_path']
        yield Prepend('JANA_PLUGIN_PATH', os.path.join(path, 'plugins'))
        yield Prepend('PATH', os.path.join(path, 'bin'))

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

    # Flags that can me made in cmake
    cmake_deps_flag_names = {
        "root": "ROOT_DIR",             # Cern root installation
        "jana": 'JANA_DIR',             # JANA2 installation directory
        'genfit': 'GENFIT_DIR',         # Genfit2  installation directory
        'eic-smear': 'EIC_SMEAR_DIR',   # EIC-smear smearing packet
        'hepmc': 'HEPMC_DIR'
    }

