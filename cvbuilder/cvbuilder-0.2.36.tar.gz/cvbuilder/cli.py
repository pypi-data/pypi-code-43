#!/usr/bin/env python3
import sys
import os

import logging

from multiprocessing import cpu_count

from colorama import init

from pathlib import Path

from cvbuilder.__version__ import __version__, __cv2version__
from cvbuilder import builder, utils, systems

import fire

init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected
from termcolor import cprint, colored

logger = logging.getLogger(__name__)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
DEFAULT_TMP = Path.home().joinpath("./temp/opencv")


def format_header():
    header = colored(
        """CVBuilder {ver} for OpenCV {cv}\n""".format(ver=__version__, cv=__cv2version__),
        "green",
        attrs=["bold"],
    )

    header += colored(
        """Python {ver.major}.{ver.minor}.{ver.micro} @ {venv}""".format(
            ver=sys.version_info, venv=sys.prefix
        ),
        "yellow",
    )

    return header


#
# def format_help(help):
#     """Formats the help string."""
#     # help = help.replace('Options:', str(crayons.white('Options:', bold=True)))
#     help = help.replace('Usage: cvbuilder', str('Usage: {0}'.format(crayons.green('cvbuilder', bold=True))))
#
#     help = help.replace('  build', str(crayons.green('  build', bold=True)))
#     help = help.replace('  system', str(crayons.yellow('  system', bold=True)))
#     help = help.replace('  dump', str(crayons.yellow('  dump', bold=False)))
#     help = help.replace('  configure', str(crayons.white('  configure', bold=False)))
#     help = help.replace('  download', str(crayons.white('  download', bold=False)))
#     help = help.replace('  make', str(crayons.white('  make', bold=False)))
#     help = help.replace('  install', str(crayons.white('  install', bold=False)))
#
#     additional_help = """
# Usage Examples:
#    Download, configure, build and install OpenCV in one step:
#    $ {build}
#    If you want to run the process again, without downloading the sources:
#    $ {clean}
#    Check other available command via:
#    $ {plain}
#    or via:
#    $ {help}
#
# Commands:""".format(**{
#         "build": crayons.green('cvbuilder build', bold=True),
#         "clean": crayons.green('cvbuilder build {}'.format(crayons.yellow("--clean", bold=True)), bold=True),
#         "plain": crayons.yellow('cvbuilder'),
#         "help": crayons.yellow('cvbuilder {}'.format(crayons.yellow('--help', bold=True)))},
#                     )
#
#     help = help.replace('Commands:', additional_help)
#
#     return help


def verify_virtual_env(value):
    if value is not None:
        current_venv = sys.exec_prefix

        if value != current_venv:
            logger.warning(
                "The virtual environment environment variable does not match the current: {} vs. {}".format(
                    colored(value, "red", attrs=["bold"]),
                    colored(current_venv, "red", attrs=["bold"]),
                )
            )

            if not value or value == "":
                return Path(current_venv)

        return Path(value)


def verify_temp_dir(value):
    if value is not None:
        tmp_dir = Path(value)

        if not tmp_dir.exists():
            tmp_dir.mkdir(parents=True)
            logging.info(
                "Created temporary to store the sources: {}".format(str(tmp_dir.resolve()))
            )

        # TODO add size check
        return tmp_dir


def system(enable_video: bool = True, enable_gui: bool = True) -> None:
    """
    Installs system dependencies
    :param enable_video: enable video capabilities
    :param enable_gui: enable GUI (GTK) capabilities
    """
    settings = ""
    settings += "video: " + colored("enabled", "green") if enable_video else "disabled"
    settings += " | gui: " + colored("enabled", "green") if enable_gui else "disabled"
    logger.info(settings)

    # TODO move to systems or cvbuilder?
    lsb = systems.get_system()
    deps = systems.get_system_dependencies(lsb)
    packages = deps.get("packages")

    install_command = packages.get("command")
    package_list = utils.select_packages(
        packages=packages, enable_gui=enable_gui, enable_video=enable_video
    )
    utils.install_packages(
        command=install_command, package_list=package_list, requires_sudo=True
    )


def download(preserve: bool = True, tempdir: Path = DEFAULT_TMP):
    """
    Downloads the OpenCV sources to the specified temporary directory.
    :param preserve: Preserve the downloaded packages.
    :param tempdir: The temporary download directory.
    :return:
    """
    settings = ""
    settings += "source: " + colored("preserve", "green") if preserve else "clean"
    settings += " | tempdir: " + colored(tempdir, "green", attrs=["bold"])
    logger.info(settings)
    tempdir = verify_temp_dir(tempdir)
    builder.download(preserve=preserve, tempdir=tempdir)


def make(tempdir: Path = DEFAULT_TMP, cpus: int = cpu_count()):
    """
    Compiles the OpenCV sources in the specified temporary directory according to the CMake configuration.
    :param tempdir: The temporary download directory.
    :param cpus: The number of CPUs to use during compilation.
    :return:
    """
    settings = ""
    settings += " | tempdir: " + colored(tempdir, "green", attrs=["bold"])
    settings += " | cpus: " + colored(cpus, "green", attrs=["bold"])
    logger.info(settings)
    tempdir = verify_temp_dir(tempdir)
    builder.build(tempdir=tempdir, cpus=cpus)


def install(tempdir: Path = DEFAULT_TMP) -> None:
    """
    Installs OpenCV from the specified temporary directory.
    :param tempdir: The temporary download directory.
    """
    settings = ""
    settings += " | tempdir: " + colored(tempdir, "green", attrs=["bold"])
    logger.info(settings)
    tempdir = verify_temp_dir(tempdir)
    builder.install(tempdir=tempdir)


def build(
    preserve: bool = True,
    tempdir: Path = DEFAULT_TMP,
    cpus: int = cpu_count(),
    verbose: bool = False,
):
    """
    Configures, makes and installs the current OpenCV version in the current (virtual) python environment.
    :param preserve: Preserve the downloaded packages
    :param tempdir: The temporary download directory.
    :param cpus: The number of CPUs to use during compilation.
    :param verbose:
    :return:
    """
    settings = ""
    settings += "source: " + colored("preserve", "green") if preserve else "clean"
    settings += " | tempdir: " + colored(tempdir, "green", attrs=["bold"])
    settings += " | cpus: " + colored(cpus, "green", attrs=["bold"])
    settings += " | verbose: " + colored(verbose, "green", attrs=["bold"])
    logger.info(settings)

    tempdir = verify_temp_dir(tempdir)
    builder.download(preserve=preserve, tempdir=tempdir)
    builder.configure(tempdir=tempdir, verbose=verbose)
    builder.build(tempdir=tempdir, cpus=cpus)
    builder.install(tempdir=tempdir)
    builder.check()


def configure(tempdir: Path = DEFAULT_TMP, verbose: bool = False):
    """
    Configures the downloaded OpenCV sources in the specified temporary directory.
    :param tempdir: The temporary download directory.
    :param verbose:
    :return:
    """
    settings = ""
    settings += " | tempdir: " + colored(tempdir, "green", attrs=["bold"])
    settings += " | verbose: " + colored(verbose, "green", attrs=["bold"])
    logger.info(settings)
    # FIXME verbosity
    verify_temp_dir(tempdir)
    build_dir = builder.configure(tempdir=tempdir, verbose=True)


def main():
    cprint(format_header(), "yellow", None, attrs=["bold"])
    fire.Fire(
        {
            "build": build,
            "check": builder.check,
            "configure": configure,
            "download": download,
            "install": install,
            "make": make,
            "dump": builder.dump,
            "system": system,
        }
    )


if __name__ == "__main__":
    main()
