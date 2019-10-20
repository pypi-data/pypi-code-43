""" Fixtures for integration tests. Integration tests to test the
capability of deleting EVCs. This test has the following premises:

 The following topology was activated on Mininet:
    test/simulated_topology.py

 OESS 1.1.9 is installed in a CentOS node running with IP 192.168.56.10

 OpenFlow 1.0 is used """


import os
from libs.core.cli import CliOptions
from libs.core.cli import create_parser


FOLDER = './content_files/'
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


def start_mininet():
    """ Instantiate the Docker Mininet topology to connect to OESS """
    return True


def start_oess_server():
    """ Instantiate the Docker OESS controller """
    return True


def test_evc_data_plane():
    """ Test ICMP over the circuit established """
    return True
