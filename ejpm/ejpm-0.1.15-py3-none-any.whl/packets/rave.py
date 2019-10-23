"""
This file provides information of how to build and configure Rave vertex finding packet:
https://github.com/WolfgangWaltenberger/rave

"""

import os

from ejpm.engine.env_gen import Set, Prepend
from ejpm.engine.recipe import Recipe
from ejpm.engine.commands import run, env, workdir


class RaveInstallation(Recipe):
    """Provides data for building and installing Rave vertex reconstruction package

    (PacketInstallationInstruction is located in recipe.py)
    """

    def __init__(self):
        # Call parent constructor to fill version, app_path ... and others
        # (!) it is called AFTER we override self.version
        super(RaveInstallation, self).__init__('rave')

        self.clone_command = ""
        self.bootstrap_command = ""         # This command is called after clone command
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

        # ENV RAVEPATH $INSTALL_DIR_RAVE

        # Git download link. Clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} " \
                             "https://github.com/WolfgangWaltenberger/rave.git {source_path}" \
            .format(**self.config)

        self.bootstrap_command = './bootstrap'

        # cmake command:
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        # (!) {{clhep_lib_dir}} and {{clhep_include_dir}} is in 2 braces. So it becomes {clhep_include_dir}
        #     on step_build the right environment will be set and we will use .format(..) again to fill them
        #     ugly? YEA!!! say hello to RAVE
        self.build_command = './configure --disable-java --prefix=$RAVEPATH ' \
                             ' LDFLAGS="-L{{clhep_lib_dir}}" ' \
                             ' CXXFLAGS="-std=c++11 -I{{clhep_include_dir}}" ' \
                             '&&   make -j{build_threads} install' \
                             "&& for f in $(ls $RAVEPATH/include/rave/*.h); do sed -i 's/RaveDllExport//g' $f; done" \
            .format(**self.config)

    def step_install(self):
        self.step_clone()
        self.step_build()

    def step_clone(self):
        """Clones RAVE from github mirror"""

        # Check the directory exists and not empty
        if os.path.exists(self.source_path) and os.path.isdir(self.source_path) and os.listdir(self.source_path):
            # The directory exists and is not empty. Nothing to do
            return
        else:
            # Create the directory
            run('mkdir -p {}'.format(self.source_path))

        run(self.clone_command)         # Execute git clone command
        workdir(self.source_path)       # Go to our build directory
        run(self.bootstrap_command)     # This command required by rave once...

    def step_build(self):
        # Create build directory

        env('RAVEPATH', self.install_path)

        # Rave uses ./configure so we building it in {source_path}
        # go to our build directory
        workdir(self.source_path)

        # environment variables CLHEP_LIB_DIR and CLHEP_INCLUDE_DIR should be set at this stage to compile it
        # otherwise we fall back to default debian install location (RHEL7 doesn't have clep in its repo)
        clhep_lib_dir = os.environ.get('CLHEP_LIB_DIR', '/usr/lib')
        clhep_include_dir = os.environ.get('CLHEP_INCLUDE_DIR', '/usr/include')

        build_command_with_clhep = self.build_command.format(
            clhep_lib_dir=clhep_lib_dir,
            clhep_include_dir=clhep_include_dir)

        # run cmake && make && install
        run(build_command_with_clhep)

    @staticmethod
    def gen_env(data):
        install_path = data['install_path']

        yield Set('RAVEPATH', install_path)
        yield Prepend('CMAKE_PREFIX_PATH', os.path.join(install_path, 'share', 'rave'))
        yield Prepend('LD_LIBRARY_PATH', os.path.join(install_path, 'lib'))

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    # The idea behind is to generate easy to use instructions: 'sudo apt-get install ... ... ... '
    os_dependencies = {
        'required': {
            'ubuntu': "autoconf shtool automake libtool",
            'centos': "autoconf shtool automake libtool"
        },
        'optional': {
            'ubuntu': "",
            'centos': ""
        },
    }
