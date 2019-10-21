""" Integration tests to test the capability of deleting EVCs. """


import os
import pytest
from libs.core.cli import CliOptions, create_parser
from libs.core.singleton import Singleton
from tests.test_integration import fixtures
from evc_manager import EvcManager


FOLDER = './tests/test_integration/content_files/'
CORRECT_CLI = ['-u', 'admin',
               '-t', 'admin',
               '-p', 'sparc123!',
               '-O', 'https://192.168.56.10/oess/',
               '-v', 'info',
               '-q']


def prepare_cli(option, source_file):
    """ Prepare CLI options adding action and source file """
    source_file = os.path.abspath(FOLDER + source_file)
    cli_options = CORRECT_CLI
    cli_options.append(option)
    cli_options.append('-f')
    cli_options.append(source_file)
    return cli_options


def start_cli(action, source_file):
    """ Prepare CLI """
    parser = create_parser()
    args = parser.parse_args(prepare_cli(action, source_file))
    return CliOptions(parser, args)


@pytest.fixture(scope="module")
def instantiate_mininet():
    """ Instantiate Mininet """
    return fixtures.start_mininet()


@pytest.fixture(scope="module")
def instantiate_docker_oess():
    """ Instantiate OESS """
    return fixtures.start_oess_server()


def instantiate_cli():
    """ Instantiate CLI """
    return start_cli('-D', 'delete_evc_incorrect_request.yaml')


def evc_manager():
    """ Instantiate EvcManager """
    return EvcManager(cli_option=instantiate_cli())


def test_delete_evc_with_error():
    """ delete EVCs """
    Singleton._instances.clear()

    with pytest.raises(ValueError):
        evc_mgr = evc_manager()
        _ = evc_mgr.delete_evcs()
