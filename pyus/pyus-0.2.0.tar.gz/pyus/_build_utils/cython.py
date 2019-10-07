import inspect
import os

from Cython.Build import cythonize
from Cython.Compiler import Options
from setuptools import Command
from setuptools.command.egg_info import egg_info

from pyus._build_utils.file_utils import find_cython_sources, copy_includes, \
    copy_and_symlink_lib


def get_ext_modules(path: str,
                    create_extension: not None,
                    compiler_options: dict = None,
                    compiler_directives: dict = None):
    """
    Returns a list of Extension objects obtained from cython sources in path
    and created with the provided create_extension function compiler options
    abd compiler directives
    options -> https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-options
    directives -> https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives
    """

    source_list = find_cython_sources(path)

    # Set some default compiler options and directives.
    # We can always define other compiler directives per file with
    # cython: boundscheck=False or locally with @cython.boundscheck(False)
    default_comiler_options = {'annotate': True, 'fast_fail': True}
    default_compiler_directives = {'embedsignature': True, 'language_level': 3}

    if compiler_options is None:
        compiler_options = {}
    if compiler_directives is None:
        compiler_directives = {}

    compiler_options.update(default_comiler_options)
    compiler_directives.update(default_compiler_directives)

    # Set the cython compiler options
    for key, value in compiler_options.items():
        if hasattr(Options, key):
            setattr(Options, key, value)
        else:
            raise ValueError("unknown Cython.Compiler.Options {}".format(key))

    ext_modules = cythonize(
        module_list=[create_extension(s) for s in source_list],
        nthreads=8,
        compiler_directives=compiler_directives,
    )

    return ext_modules


class InstallLibCommand(Command):

    user_options = [
        ('lib-name=', None, 'library name'),
        ('lib-version=', None, 'library version'),
        ('inc-path=', None, 'path to include folder'),
        ('lib-path=', None, 'path to lib folder')
    ]

    _lib_name = None
    _lib_version = None
    _inc_path = None
    _lib_path = None
    _lib_dst_path = None # To be set by a derived class

    def initialize_options(self):
        self.lib_name = None
        self.lib_version = None
        self.inc_path = None
        self.lib_path = None

    def finalize_options(self):

        custom_options = ['lib_name', 'lib_version', 'inc_path', 'lib_path']

        # Store custom user options during first call to finalize_otions() to
        # prevent loosing them if reinitialize_command() is called
        for opt in custom_options:
            if getattr(self, '_' + str(opt)) is None:
                setattr(self, '_' + str(opt), getattr(self, opt))


            # Check if user has provided options
            if getattr(self, '_' + str(opt)) is None:
                raise ValueError("""
            Please provide {st} arg in setup.cfg, i.e.:
            [install_libso]
            {st}=<value> 
            """.format(st=opt))

        # Check if lib dst path is provided
        if self._lib_dst_path is None:
            raise ValueError('no destination path provided, please subclass the '
                             'InstallLibCommand class and set the attribute '
                             '_lib_dst_path')

    def run(self):
        # TODO: Add function to check if lib present in inc and lib path cooresponds
        #  to the name and version provided
        copy_includes(self._inc_path, self._lib_dst_path)
        copy_and_symlink_lib(self._lib_path, self._lib_dst_path)


class EggInfoCommand(egg_info):
    """
    Custom egg_info command to call the install_pulse command.
    The call to install_pulse command is put in egg_info because egg_info is
    called in each used way of installing the package (pip install, pip install -e,
    pip wheel, python setup.py install, python setup.py develop, python setup.py
    wheel), and it is called early enough in the build process so the sources
    downloaded from libpulse location are included in the wheel archive
    """

    def run(self):
        self.run_command('install_libso')
        egg_info.run(self)


# TODO: Remove bdist_wheel command, to move the wheels in the NAS, we should use
#  a post build/install script that moves them.
#  Moreover, pip install fails with this command because it looses the track
#  of the wheel due to the dist-dir modification
# class BdistWheelCommand(bdist_wheel):
#     """
#     Subclass of bdist_wheel to add a custom modification of final path of built
#     distribution.
#     To do so, add the --dist-dir <path> when running python setup.py bdist_wheel
#     If you do not use the option, the wheel will be placed in <project-dir>/dist
#     """
#
#     # user_options = bdist_wheel.user_options + [
#     #     ('cuda-version=', None, 'CUDA version the library is built against')
#     # ]
#
#     def initialize_options(self):
#         print('------------------- INIT COMANND BDIST WHEEL ------------------')
#         bdist_wheel.initialize_options(self)
#         self.cuda_version = None
#
#     def finalize_options(self):
#         print('------------------- FINALIZE COMANND BDIST WHEEL ------------------')
#         bdist_wheel.finalize_options(self)
#
#         # WIP:
#         # This gets the cuda version from install_pulse arguments. If no argument
#         # is provided to install_pulse, self.cuda_version defaults to None (same
#         # as install_pulse command
#         # https://stackoverflow.com/questions/30191631/referring-to-existing-distutils-options-inside-setup-cfg-and-setup-py?answertab=votes#tab-top
#         from setuptools.dist import Distribution
#         dist = Distribution()
#         dist.parse_config_files()
#         try:
#             self.cuda_version = dist.get_option_dict('install_pulse')['cuda_version'][1]
#         except KeyError:
#             pass
#
#         # Complete path where to put final built distribution depending on versioning
#         self.dist_dir = os.path.join(
#             self.dist_dir, 'pyus-{}'.format(pyus_version),
#             'cu' + check_cuda_version(self.cuda_version)[0].replace(".", "")
#         )
#
#     def run(self):
#         print('------------------- RUN COMANND BDIST WHEEL ------------------')
#         bdist_wheel.run(self)