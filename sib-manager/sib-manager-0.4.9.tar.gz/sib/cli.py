import click
import os
import sys
import logging
from urllib.parse import urlparse
from . import __version__
from .project import Project
from .package import Package
from .client import Client


logger = logging.getLogger(__name__)


# click entrypoint
@click.group()
@click.option('-v', '--verbose', count=True, help='Set verbosity level.')
@click.version_option(__version__)
def main(verbose):

    """Startin'Blox installer"""

    # set log level
    if verbose == 2:
        logging.basicConfig(level='DEBUG', format='%(levelname)s:%(module)s:%(message)s')
    elif verbose == 1:
        logging.basicConfig(level='INFO', format='[%(levelname)s]: %(message)s')
    else:
        logging.basicConfig(level='WARNING', format='[%(levelname)s]: %(message)s')


@main.command()
@click.argument('name', nargs=1)
@click.argument('directory', required=False)
@click.option('--production', is_flag=True, default=False, help='Use a production template')
def startproject(name, production, directory):

    """Start a new startin'blox project"""

    # set absolute path to project directory
    if directory:
        directory = os.path.abspath(directory)
    else:
        # set a directory from project name in pwd
        directory = os.path.join(os.getcwd(), name)

    project = Project(name, directory)
    project.create(production)


@main.command()
@click.argument('name', nargs=1)
@click.argument('directory', required=False)
def install(name, directory):

    """Initialize a startin'blox project"""

    # set absolute path to project directory
    if directory:
        directory = os.path.abspath(directory)
    else:
        # get path from current dir
        directory = os.getcwd()

    project = Project(name, directory)
    project.install()
    project.load()


@main.command()
@click.argument('directory', nargs=1)
def startapp(directory):

    """Create  a new startin'blox client app"""

    client = Client(directory)
    client.install()
    client.compile()

@main.command()
@click.argument('name', nargs=1)
@click.argument('directory', required=False)
def startpackage(name, directory):

    """Create a new startin'blox package"""

    # set absolute path to package directory (given directory is the project path)
    if directory:
        directory = os.path.join(os.path.abspath(directory), name)
    else:
        # get path from current dir
        directory = os.path.join(os.getcwd(), name)

    package = Package(name, directory)
    package.create()
