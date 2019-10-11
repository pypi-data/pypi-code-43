# Instructions based on http://www.pyimagesearch.com/2015/10/26/how-to-install-opencv-3-on-raspbian-jessie/
# and https://docs.opencv.org/trunk/d7/d9f/tutorial_linux_install.html
# and https://stackoverflow.com/questions/20953273/install-opencv-for-python-3-3
import sys
import sysconfig
import logging
from pathlib import Path
from pprint import pformat
from termcolor import cprint, colored
from .__version__ import __cv2version__
from . import utils, systems

logger = logging.getLogger(__name__)

OPENCV_SOURCE_URL = "https://github.com/Itseez/opencv/archive/{}.zip".format(__cv2version__)
OPENCV_CONTRIB_URL = "https://github.com/Itseez/opencv_contrib/archive/{}.zip".format(
    __cv2version__
)


def get_environment() -> dict:
    packages = Path(sysconfig.get_path("platlib"))
    numpy_path = sys.modules.get("numpy")

    if not numpy_path:
        numpy_path = packages.joinpath("numpy")

    multiarch = sysconfig.get_config_var("multiarchsubdir")  # raspi
    libdir = sysconfig.get_config_var("LIBDIR")
    py3lib = sysconfig.get_config_var("LDLIBRARY")

    if multiarch:
        # FIXME relative path addition
        libpython = Path(libdir).joinpath("." + multiarch).joinpath(py3lib)
    else:
        libpython = Path(libdir).joinpath(py3lib)

    env = {
        "libpython": libpython,
        "prefix": Path(sys.exec_prefix),
        "executable": Path(sys.executable),
        "include": Path(sysconfig.get_path("include")),
        "packages": packages,
        "numpy_include": numpy_path.joinpath("core/include"),
        "platform": sysconfig.get_platform(),
    }

    if not env.get("include").exists():
        # virtual envs created with venv module obviously do not create a symlink to include
        env["include"] = Path(sysconfig.get_path("platinclude"))
        logger.info("Using system include directory!")

    for key, value in env.items():
        if isinstance(value, Path) and not value.exists():
            raise FileNotFoundError("File or directory not found: '{}'!".format(str(value)))

    env.setdefault(
        "libcv2", packages.joinpath("cv2{}".format(sysconfig.get_config_var("EXT_SUFFIX")))
    )

    return env


def get_cmake_configuration(libraries: dict, tempdir: Path):
    contrib_modules = get_opencv_contrib_folder(tempdir=tempdir).joinpath("modules")

    env = get_environment()

    tesseract_include = Path(libraries.get("tesseract").get("include"))

    config = {
        "contrib_modules": contrib_modules,
        "python3_executable": env.get("executable"),
        "python3_library": env.get("libpython"),
        "python3_packages": env.get("packages"),
        "python3_include": env.get("include"),
        "python3_numpy_include": env.get("numpy_include"),
        "python3_cv2_library": env.get("libcv2"),
        "tesseract_include_dir": tesseract_include,
        # using virtual environment as install target -> "/usr/local" requires sudo rights!
        "cv2_install_prefix": env.get("prefix"),  # "/usr/local"
    }

    logger.info("{}: {}".format(colored("Configuration", "yellow"), config))

    return config


def cmake(build_directory: Path, config: dict, verbose: bool = False):
    d_settings = {
        "BUILD_EXAMPLES": "ON",
        "BUILD_JAVA": "OFF",
        "BUILD_opencv_js": "OFF",
        "BUILD_opencv_python3": "ON",
        "BUILD_TESTS": "OFF",
        "BUILD_PERF_TESTS": "OFF",
        "BUILD_SHARED_LIBS": "NO",
        "CMAKE_BUILD_TYPE": "RELEASE",
        "CMAKE_INSTALL_PREFIX": config["cv2_install_prefix"],
        "CMAKE_VERBOSE_MAKEFILE": "ON",
        "ENABLE_PYLINT": "OFF",
        "INSTALL_C_EXAMPLES": "OFF",
        "INSTALL_PYTHON_EXAMPLES": "ON",
        "INSTALL_TESTS": "OFF",
        "OPENCV_ENABLE_NONFREE": "ON",
        "OPENCV_EXTRA_MODULES_PATH": config["contrib_modules"],
        "OPENCV_SKIP_PYTHON_LOADER": "ON",
        "OPENCV_PYTHON3_INSTALL_PATH:PATH": config["python3_packages"],
        "PYTHON2_EXECUTABLE:FILEPATH": "",
        "PYTHON2_INCLUDE_DIR:PATH": "",
        "PYTHON2_INCLUDE_DIR2:PATH": "",
        "PYTHON2_LIBRARY:FILEPATH": "",
        "PYTHON2_LIBRARY_DEBUG:FILEPATH": "",
        "PYTHON2_NUMPY_INCLUDE_DIRS:PATH": "",
        "PYTHON2_PACKAGES_PATH:PATH": "",
        "PYTHON3_EXECUTABLE:PATH": config["python3_executable"],
        "PYTHON3_INCLUDE_DIR:PATH": config["python3_include"],
        "PYTHON3_LIBRARY:FILEPATH": config["python3_library"],
        "PYTHON3_LIBRARY_DEBUG:FILEPATH": "",
        "PYTHON3_NUMPY_INCLUDE_DIRS:PATH": config["python3_numpy_include"],
        "PYTHON3_PACKAGES_PATH:PATH": config["python3_packages"],
        "PYTHON_DEFAULT_EXECUTABLE:FILEPATH": config["python3_executable"],
        "PYTHON_NUMPY_INCLUDE_DIRS:PATH": config["python3_numpy_include"],
        "PYTHON_PACKAGES_PATH:PATH": config["python3_packages"],
        "Tesseract_INCLUDE_DIR:PATH": config["tesseract_include_dir"],
        "WITH_FFMPEG": "ON",
        "WITH_MATLAB": "OFF",
        "WITH_OPENCL": "ON",
        # workaround until upstream https://github.com/opencv/opencv/issues/15157 is fixed
        "EIGEN_INCLUDE_PATH:PATH": "/usr/include/eigen3",
    }
    if verbose:
        d_settings.setdefault("CMAKE_VERBOSE_MAKEFILE", "ON")  # this helps debugging

    # additional -D settings generated manually via cmake-gui by dropping python2 settings
    # and according to https://github.com/opencv/opencv/issues/13202
    cmake_args = " ".join([f"-D {key}={value}" for key, value in d_settings.items()])

    cmd = "cmake {} ..".format(cmake_args)

    utils.run_process(cmd, requires_sudo=False, cwd=build_directory)
    return


def make(build_directory: Path, cpus: int = 1):
    utils.run_process("make clean", requires_sudo=False, cwd=build_directory)
    cmd = "make -j{}".format(cpus)
    utils.run_process(cmd, requires_sudo=False, cwd=build_directory)


def make_install(build_directory: Path, requires_sudo: bool):
    utils.run_process("make install", requires_sudo=requires_sudo, cwd=build_directory)
    if requires_sudo:
        utils.run_process("/sbin/ldconfig", requires_sudo=requires_sudo, cwd=build_directory)


def get_opencv_zip_location(tempdir: Path):
    return tempdir.joinpath("opencv.zip")


def get_contrib_zip_location(tempdir: Path):
    return tempdir.joinpath("opencv_contrib.zip")


def get_opencv_folder(tempdir: Path) -> Path:
    return tempdir.joinpath("opencv-{}".format(__cv2version__))


def get_opencv_contrib_folder(tempdir: Path) -> Path:
    return tempdir.joinpath("opencv_contrib-{}".format(__cv2version__))


def download(preserve: bool, tempdir: Path) -> tuple:
    opencv_zip = get_opencv_zip_location(tempdir=tempdir)
    contrib_zip = get_contrib_zip_location(tempdir=tempdir)

    unzipped_folder_opencv = get_opencv_folder(tempdir=tempdir)
    unzipped_folder_opencv_contrib = get_opencv_contrib_folder(tempdir=tempdir)

    utils.download_unzip_clean(
        url=OPENCV_SOURCE_URL,
        target=opencv_zip,
        absolute_directory=unzipped_folder_opencv,
        tmp_dir=tempdir,
        keep_target_file=preserve,
    )
    utils.download_unzip_clean(
        url=OPENCV_CONTRIB_URL,
        target=contrib_zip,
        absolute_directory=unzipped_folder_opencv_contrib,
        tmp_dir=tempdir,
        keep_target_file=preserve,
    )
    return


def configure(tempdir: Path, verbose: bool = False) -> Path:
    lsb = systems.get_system()
    deps = systems.get_system_dependencies(lsb)
    libraries = deps.get("libraries")

    cmake_config = get_cmake_configuration(libraries=libraries, tempdir=tempdir)

    build_dir = get_build_dir(tempdir)
    cmake(build_directory=build_dir, config=cmake_config, verbose=verbose)

    return build_dir


def get_build_dir(tempdir):
    build_dir = get_opencv_folder(tempdir=tempdir).joinpath("build")
    if not build_dir.exists():
        logger.warning("Creating build directory: {}".format(str(build_dir)))
        build_dir.mkdir()
    return build_dir


def build(tempdir: Path, cpus: int):
    build_dir = get_build_dir(tempdir=tempdir)
    make(build_directory=build_dir, cpus=cpus)


def install(tempdir: Path):
    build_dir = get_build_dir(tempdir=tempdir)
    make_install(build_directory=build_dir, requires_sudo=False)


def check():
    """
    Checks whether OpenCV is correctly configured.
    """
    try:
        import cv2

        logger.info(
            "OpenCV {} loaded from {}".format(
                colored(cv2.__version__, "green", attrs=["bold"]), cv2.__file__
            )
        )
        build_info = cv2.getBuildInformation()
        logger.info(build_info)

        if cv2.__version__ != __cv2version__:
            raise AssertionError(
                "The imported OpenCV version '{}' does not equal the expected one '{}'".format(cv2.__version__,
                                                                                               __cv2version__))

    except ModuleNotFoundError as me:
        logger.info("CV2 could not be imported")
        cv2_install_location = get_environment().get("libcv2")
        if not cv2_install_location.exists():
            raise ReferenceError(
                "The built library was expected to be located at '{}', please check system location.".format(
                    str(cv2_install_location)
                )
            )
    return True


def dump():
    """
    Dumps environment and system information.
    """
    env = get_environment()
    format_left_align = "{{:{}}} {{}}".format(max([len(key) for key in env.keys()]) + 1)
    pyenv = [
        format_left_align.format(key + ":", value) for key, value in get_environment().items()
    ]
    logger.info("Python environment:")
    logger.info("\n".join(pyenv))

    lsb = systems.get_system()
    logger.info(
        "System: {} {}".format(
            colored(lsb.id, "green"), colored(lsb.name, "green", attrs=["bold"])
        )
    )

    deps = systems.get_system_dependencies(lsb)
    logger.info("Dependencies: {}".format(pformat(deps)))

    try:
        out = utils.check_output("make --version; exit 0", shell=True)
        ver = out[0]
        logger.info(ver)
    except BaseException as be:
        logger.info("Cannot find 'make' command")

    try:
        out = utils.check_output("cmake --version; exit 0", shell=True)
        ver = out[0]
        logger.info(ver)
    except BaseException as be:
        logger.info("Cannot find 'cmake' command")
