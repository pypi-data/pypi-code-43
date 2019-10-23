"""
This file provides information of how to build and configure CERN.ROOT:
https://github.com/root-project/root

"""

import os
from distutils.dir_util import mkpath

from ejpm.engine import env_gen
from ejpm.engine.recipe import Recipe
from ejpm.engine.commands import run, env, workdir, is_not_empty_dir

ROOTSYS = "ROOTSYS"


class RootInstallation(Recipe):
    """Provides data for building and installing root

    PackageInstallationContext is located in engine/recipe.py

    """

    class DefaultConfigFields(object):
        pass

    def __init__(self):
        """
        """

        # Fill the common path pattern
        super(RootInstallation, self).__init__("root")
        self.config['branch'] = 'v{}-{:02}-{:02}'.format(6, 18, 0)

    def find_python(self):
        from subprocess import check_output
        out = check_output(["which", "python3"]).decode('ascii').strip()

        if not out:
            out = check_output(["which", "python2"]).decode('ascii').strip()

        if not out:
            out = check_output(["which", "python"]).decode('ascii').strip()
        return out

    def setup(self):
        """Sets all variables like source dirs, build dirs, etc"""

        #
        # Compile with python3, then whatever python is...
        python_path = self.find_python()
        self.config["python_flag"] = ' -DPYTHON_EXECUTABLE={} '.format(python_path) if python_path else ''
        # >oO debug: print("Configuring ROOT with '{}' python flag".format(self.config["python_flag"]))

        #
        # use_common_dirs_scheme sets standard package variables:
        # version      = 'v{}-{:02}-{:02}'                 # Stringified version. Used to create directories and so on
        # source_path  = {app_path}/src/{version}          # Where the sources for the current version are located
        # build_path   = {app_path}/build/{version}        # Where sources are built. Kind of temporary dir
        # install_path = {app_path}/root-{version}         # Where the binary installation is
        self.use_common_dirs_scheme()

        #
        # Root download link. We will use github root mirror:
        # The tags have names like: v6-14-04
        # http://github.com/root-project/root.git
        # clone with shallow copy
        self.clone_command = "git clone --depth 1 -b {branch} https://github.com/root-project/root.git {source_path}" \
            .format(**self.config)

        # Make sure custom flags are in there
        if "cmake_custom_flags" not in self.config:
            self.config["cmake_custom_flags"] = ''

        #
        # ROOT packets to disable in our build (go with -D{name}=ON flag)
        # the  -Wno-dev  flag is to ignore the project developers cmake warnings for policy CMP0075
        self.build_cmd = "cmake -Wno-dev -DCMAKE_INSTALL_PREFIX={install_path} " \
                         " -Dgdml=ON" \
                         " -Dminuit2=ON" \
                         " {python_flag}" \
                         " {cmake_custom_flags}" \
                         " {source_path}" \
                         "&& cmake --build . -- -j {build_threads}" \
                         "&& cmake --build . --target install" \
            .format(**self.config)  # make global options like '-j8'. Skip now

    def step_install(self):
        self.step_clone_root()
        self.step_build_root()

    def step_clone_root(self):
        """Clones root from github mirror"""

        # Check the directory exists and not empty
        if is_not_empty_dir(self.source_path):
            return  # The directory exists and is not empty. Assume it cloned

        mkpath(self.source_path)  # Create the directory and any missing ancestor directories if not there
        run(self.clone_command)  # Execute git clone command

    def step_build_root(self):
        """Builds root from the ground"""

        # Create build directory
        run('mkdir -p {}'.format(self.build_path))

        env('ROOTSYS', self.install_path)

        # go to our build directory
        workdir(self.build_path)

        # run cmake && make && install
        run(self.build_cmd)

    def step_rebuild_root(self):
        """Clear root build directory"""

        # clear sources directories if needed
        run('rm -rf {}'.format(self.source_path))
        run('rm -rf {}'.format(self.build_path))

        # Now run build root
        self.step_build_root()

    @staticmethod
    def gen_env(data):
        install_path = data['install_path']

        def update_python_environment():
            """Function that will update ROOT environment in python
            We need this function because we DON'T want source thisroot in python
            """

            root_bin = os.path.join(install_path, 'bin')
            root_lib = os.path.join(install_path, 'lib')
            root_jup = os.path.join(install_path, 'etc', 'notebook')

            env_updates = [
                env_gen.Set('ROOTSYS', install_path),
                env_gen.Prepend('PATH', root_bin),
                env_gen.Prepend('LD_LIBRARY_PATH', root_lib),
                env_gen.Prepend('DYLD_LIBRARY_PATH', root_lib),
                env_gen.Prepend('PYTHONPATH', root_lib),
                env_gen.Prepend('CMAKE_PREFIX_PATH', install_path),
                env_gen.Prepend('JUPYTER_PATH', root_jup),
            ]

            for updater in env_updates:
                updater.update_python_env()

        # We just call thisroot.xx in different shells
        bash_thisroot = os.path.join(install_path, 'bin', 'thisroot.sh')
        csh_thisroot = os.path.join(install_path, 'bin', 'thisroot.csh')

        raw = env_gen.RawText(
            # Bash
            'if test -f "{0}"; then source {0}; fi'.format(bash_thisroot),

            # Tcsh
            """
            if ( ! -f {0} ) then
                source {0}
            endif
            """.format(csh_thisroot),

            # Python
            update_python_environment
        )
        yield raw

    #
    # OS dependencies are a map of software packets installed by os maintainers
    # The map should be in form:
    # os_dependencies = { 'required': {'ubuntu': "space separated packet names", 'centos': "..."},
    #                     'optional': {'ubuntu': "space separated packet names", 'centos': "..."}
    #                   }
    os_dependencies = {
        'required': {
            'ubuntu': "git dpkg-dev cmake g++ gcc binutils libx11-dev libxpm-dev libxft-dev libxext-dev",
            'centos': "git cmake gcc-c++ gcc binutils libX11-devel libXpm-devel libXft-devel libXext-devel"
        },
        'optional': {
            'ubuntu': "gfortran libssl-dev libpcre3-dev "
                      "xlibmesa-glu-dev libglew1.5-dev libftgl-dev "
                      "libmysqlclient-dev libfftw3-dev libcfitsio-dev "
                      "graphviz-dev libavahi-compat-libdnssd-dev "
                      "libldap2-dev python-dev libxml2-dev libkrb5-dev "
                      "libgsl0-dev libqt4-dev",

            'centos': "gcc-gfortran openssl-devel pcre-devel "
                      "mesa-libGL-devel mesa-libGLU-devel glew-devel ftgl-devel mysql-devel "
                      "fftw-devel cfitsio-devel graphviz-devel "
                      "avahi-compat-libdns_sd-devel libldap-dev python-devel "
                      "libxml2-devel gsl-static"
        },
    }

    # (!) Those are not used at the moment. But there is an idea to have minimized version of root
    root_mini_flags = [
        "afdsmgrd           = OFF",  # Dataset manager for PROOF-based analysis facilities
        "afs                = OFF",  # AFS support, requires AFS libs and objects
        "alien              = OFF",  # ON  - AliEn support, requires libgapiUI from ALICE
        "all                = OFF",  # OFF - Enable all optional components
        "asimage            = OFF",  # ON  - Image processing support, requires libAfterImage
        "astiff             = OFF",  # ON  - Include tiff support in image processing
        "bonjour            = OFF",  # ON  - Bonjour support, requires libdns_sd and/or Avahi
        "builtin_afterimage = ON ",  # ON  - Built included libAfterImage, or use system libAfterImage
        "builtin_fftw3      = ON",  # OFF - Built the FFTW3 library internally (downloading tarfile from the Web)
        "builtin_ftgl       = ON ",  # ON  - Built included libFTGL, or use system libftgl
        "builtin_freetype   = OFF",  # OFF - Built included libfreetype, or use system libfreetype
        "builtin_glew       = ON ",  # ON  - Built included libGLEW, or use system libGLEW
        "builtin_pcre       = OFF",  # OFF - Built included libpcre, or use system libpcre
        "builtin_zlib       = OFF",  # OFF - Built included libz, or use system libz
        "builtin_lzma       = OFF",  # OFF - Built included liblzma, or use system liblzma
        "builtin_davix      = OFF",  # OFF - Built the Davix library internally (downloading tarfile from the Web)
        "builtin_gsl        = OFF",  # OFF - Built the GSL library internally (downloading tarfile from the Web)
        "builtin_cfitsio    = OFF",  # OFF - Built the FITSIO library internally (downloading tarfile from the Web)
        "builtin_xrootd     = OFF",  # OFF - Built the XROOTD internally (downloading tarfile from the Web)
        "builtin_llvm       = ON ",  # ON  - Built the LLVM internally
        "builtin_tbb        = ON ",  # OFF - Built the TBB internally

        "cxx11              = ON ",  # ON  - Build using C++11 compatible mode, requires gcc > 4.7.x or clang
        "cxx14              = OFF",  # OFF - Build using C++14 compatible mode, requires gcc > 4.9.x or clang
        "cxx17              = OFF",  # OFF - Build using C++17 compatible mode, requires gcc > 7.1.x or clang

        "libcxx             = OFF",  # OFF - Build using libc++, requires cxx11 option
        "castor             = OFF",  # ON  - CASTOR support, requires libshift from CASTOR >               =  1.5.2
        "ccache             = OFF",  # OFF - Enable ccache usage for speeding up builds
        "chirp              = OFF",  # ON  - Chirp support (Condor remote I/O), requires libchirp_client
        "cling              = ON ",  # ON  - Enable new CLING C++ interpreter
        # "cocoa              = *  ",  # *   - Use native Cocoa/Quartz graphics backend (MacOS X only)
        # "davix              = *  ",  # *   - DavIx library for HTTP/WEBDAV access
        "dcache             = OFF",  # ON  - dCache support, requires libdcap from DESY
        "exceptions         = ON ",  # ON  - Turn on compiler exception handling capability
        "explicit link      = *  ",  # *   - Explicitly link with all dependent libraries
        "fail-on-missing    = ON ",  # OFF - Fail the configure step if a required external package is missing
        "fftw3              = ON ",  # ON  - Fast Fourier Transform support, requires libfftw3
        "fitsio             = OFF",  # ON  - Read images and data from FITS files, requires cfitsio

        "gdml               = ON ",  # *   - GDML writer and reader
        "geocad             = OFF",  # OFF - ROOT-CAD Interface
        "genvector          = ON ",  # ON  - Build the new libGenVector library
        "gfal               = OFF",  # ON  - GFAL support, requires libgfal
        "glite              = OFF",  # ON  - gLite support, requires libglite-api-wrapper
        "globus             = OFF",  # OFF - Globus authentication support, requires Globus toolkit
        "gminimal           = OFF",  # OFF - Do not automatically search for support libraries, but include X11
        "gnuinstall         = OFF",  # OFF - Perform installation following the GNU guidelines
        "gsl_shared         = OFF",  # OFF - Enable linking against shared libraries for GSL (default no)
        "gviz               = OFF",  # ON  - Graphs visualization support, requires graphviz
        "hdfs               = OFF",  # ON  - HDFS support; requires libhdfs from HDFS >               =  0.19.1
        "http               = ON ",  # *   - HTTP Server support
        "imt                = ON ",  # ON  - Enable ROOT Multithreading Capabilities (default ON from version 6.10)
        "jemalloc           = OFF",  # OFF - Using the jemalloc allocator
        "krb5               = OFF",  # ON  - Kerberos5 support, requires Kerberos libs
        "ldap               = OFF",  # ON  - LDAP support, requires (Open)LDAP libs
        "mathmore           = ON ",  # ON  - Build the new libMathMore
        "memstat            = OFF",  # *   - A memory statistics utility, helps to detect memory leaks
        "minimal            = ON ",  # OFF - Do not automatically search for support libraries
        "minuit2            = ON ",  # *   - Build the new libMinuit2 minimizer library
        "monalisa           = OFF",  # ON  - Monalisa monitoring support, requires libapmoncpp
        "mt                 = OFF",  # OFF - Multi-threading support (deprecated and unused since ROOT v6.12)
        "mysql              = OFF",  # ON  - MySQL support, requires libmysqlclient
        "odbc               = OFF",  # ON  - ODBC support, requires libiodbc or libodbc
        "opengl             = OFF",  # ON  - OpenGL support, requires libGL and libGLU
        "oracle             = OFF",  # ON  - Oracle support, requires libocci
        "pgsql              = OFF",  # ON  - PostgreSQL support, requires libpq
        "pythia6            = OFF",  # ON  - Pythia6 EG support, requires libPythia6
        "pythia6_nolink     = OFF",  # OFF - Delayed linking of Pythia6 library
        "pythia8            = OFF",  # ON  - Pythia8 EG support, requires libPythia8
        "python             = ON ",  # ON  - Python ROOT bindings, requires python > = 2.2
        # "qt                    ",  # NA  - Qt graphics backend, requires libqt > = 4.8
        # "qtgsi              = *",  # *   - GSI's Qt integration, requires libqt > = 4.8
        "roofit             = ON ",  # *   - Build the libRooFit advanced fitting package
        "root7              = OFF",  # OFF - ROOT 7 support (read more)
        "roottest           = OFF",  # OFF - Include roottest in the test suit, if roottest exists in root
        "ruby               = OFF",  # OFF - Ruby ROOT bindings, requires ruby >= 1.8
        "r                  = OFF",  # OFF - R ROOT bindings, requires R, Rcpp and RInside
        "rfio               = OFF",  # ON  - RFIO support, requires libshift from CASTOR >= 1.5.2
        "rpath              = OFF",  # OFF - Set run-time library load path on executables and shared libraries
        "sapdb              = OFF",  # ON  - MaxDB/SapDB support, requires libsqlod and libsqlrte
        "shadowpw           = OFF",  # ON  - Shadow password support
        "shared             = OFF",  # ON  - Use shared 3rd party libraries if possible
        "soversion          = OFF",  # OFF - Set version number in sonames (recommended)
        "sqlite             = OFF",  # ON  - SQLite support, requires libsqlite3
        "srp                = OFF",  # ON  - SRP support, requires SRP source tree
        "ssl                = OFF",  # ON  - SSL encryption support, requires openssl
        "tbb                = OFF",  # OFF - TBB multi-threading support, requires TBB
        "table              = OFF",  # *   - Build libTable contrib library
        "tcmalloc           = OFF",  # OFF - Using the tcmalloc allocator
        "testing            = OFF",  # OFF - Enable test suit of ROOT with CTest
        "thread             = ON ",  # ON  - Using thread library (cannot be disabled)
        "tmva               = ON ",  # ON  - Build TMVA multi variate analysis library
        "unuran             = OFF",  # *   - UNURAN - package for generating non-uniform random numbers
        # "vc               = *  ",  # *   - Vc adds a few new types for portable and intuitive SIMD programming
        "vdt                = ON ",  # ON  - VDT adds a set of fast and vectorisable mathematical functions
        "winrtdebug         = OFF",  # OFF - Link against the Windows debug runtime library
        "xft                = OFF",  # ON  - Xft support (X11 antialiased fonts)
        "xml                = ON ",  # ON  - XML parser interface
        "xrootd             = OFF",  # ON  - Build xrootd file server and its client (if supported)
        "x11                = OFF",  # *   - X11 support

        "runtime_cxxmodules = OFF",  # OFF - Enable runtime c++ modules
    ]


def root_find():
    """Looks for CERN ROOT package
    :return [str] - empty list if not found or a list with 1 element - ROOTSYS path

    The only way to find ROOT is by checking for ROOTSYS package,
    The function family xxx_find() return list in general
    so this function returns ether empty list or a list with 1 element - root path
    """

    # The only way to find a CERN ROOT is by
    result = []

    # Check ROOTSYS environment variable
    if ROOTSYS not in os.environ:
        print("<red>ROOTSYS</red> not found in the environment")
        return result

    # Now check ROOTSYS exists in the system
    root_sys_path = os.environ[ROOTSYS]
    if not os.path.isdir(root_sys_path):
        print("WARNING", " ROOTSYS points to nonexistent directory of a file")
        return result

    # Looks like root exists, return the path
    return [root_sys_path]
