"""
This file provides information of how to build and configure CLHEP library:
https://gitlab.cern.ch/CLHEP/CLHEP

"""

import os

from ejpm.engine.commands import run, workdir
from ejpm.engine.env_gen import Set, Append, Prepend
from ejpm.engine.recipe import Recipe


class ClhepInstallation(Recipe):
    """Provides data for building and installing CLHEP framework
    """

    def __init__(self):

        # Set initial values for parent class and self
        super(ClhepInstallation, self).__init__('clhep')
        self.clone_command = ''             # will be set by self.set_app_path
        self.build_cmd = ''                 # will be set by self.set_app_path
        self.config['branch'] = 'master'

    def setup(self):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # use_common_dirs_scheme sets standard package variables:
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme()

        #
        # Git download link. Clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} https://gitlab.cern.ch/CLHEP/CLHEP.git {source_path}"\
            .format(**self.config)

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCLHEP_SINGLE_THREAD=ON -DCMAKE_INSTALL_PREFIX={install_path} {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
                         .format(**self.config)   # make global options like '-j8'. Skip now

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

        path = data['install_path']
        lib_path = os.path.join(path, 'lib')
        include_path = os.path.join(path, 'include')
        bin_path = os.path.join(path, 'bin')

        yield Set('CLHEP', path)
        yield Set('CLHEP_BASE_DIR', path)                  # Some system look for CLHEP this way
        yield Set('CLHEP_INCLUDE_DIR', include_path)  # or /usr/include/CLHEP/
        yield Set('CLHEP_LIB_DIR', lib_path)

        yield Prepend('PATH', bin_path)  # to make available clhep-config and others
        yield Prepend('LD_LIBRARY_PATH', lib_path)

        # set DYLD_LIBRARY_PATH for mac
        import platform
        if platform.system() == 'Darwin':
            yield Append('DYLD_LIBRARY_PATH', lib_path)

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "cmake",
            'centos': "cmake"
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }
