#!/usr/bin/env python3
"""Class used to create the configuration file used for unittesting.

NOTE!! This script CANNOT import any pattoo-shared libraries. Doing so risks
libraries trying to access a configuration or configuration directory that
doesn't yet exist. This is especially important when running cloud based
automated tests such as 'Travis CI'.

"""

# Standard imports
from __future__ import print_function
import tempfile
import os
import sys
import yaml

# Try to create a working PYTHONPATH
DEV_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(
    os.path.abspath(os.path.join(DEV_DIR, os.pardir)), os.pardir))
if DEV_DIR.endswith('/pattoo-shared/tests/dev') is True:
    sys.path.append(ROOT_DIR)
else:
    print(
        'This script is not installed in the "tests/dev" directory. '
        'Please fix.')
    sys.exit(2)

# Initialize GLOBAL variables
CONFIG_SUFFIX = '.pattoo-shared-unittests/config'
CONFIG_DIRECTORY = '{}/{}'.format(os.environ['HOME'], CONFIG_SUFFIX)

# Pattoo imports
from pattoo_shared import log


class TestConfig(object):
    """Creates configuration for testing."""

    def __init__(self):
        """Initialize the class."""
        # Set global variables
        self._log_directory = tempfile.mkdtemp()
        self._cache_directory = tempfile.mkdtemp()
        self._daemon_directory = tempfile.mkdtemp()

        # Make sure the environmental variables are OK
        _environment()

        # Make sure the configuration directory is OK
        self._config_directory = CONFIG_DIRECTORY
        if os.path.isdir(CONFIG_DIRECTORY) is False:
            os.makedirs(CONFIG_DIRECTORY, mode=0o750, exist_ok=True)

        self._config = {
            'main': {
                'log_directory': self._log_directory,
                'log_level': 'debug',
                'cache_directory': self._cache_directory,
                'daemon_directory': self._daemon_directory,
                'polling_interval': 20
            },
            'pattoo-api-agentd': {
                'api_ip_address': '127.0.0.1',
                'api_ip_bind_port': 6060,
                'api_uses_https': False
            },
            'pattoo-agent-snmpd': {
                'oid_groups': [
                    {
                        'group_name': 'TEST',
                        'ip_devices': ['localhost'],
                        'oids': ['.1.3.6.1.2.1.2.2.1.10',
                                 '.1.3.6.1.2.1.2.2.1.16']
                    }
                ],
                'snmp_groups': [
                    {
                        'group_name': 'TEST',
                        'snmp_authpassword': None,
                        'snmp_authprotocol': None,
                        'snmp_community': 'public',
                        'snmp_port': 161,
                        'snmp_privpassword': None,
                        'snmp_privprotocol': None,
                        'snmp_secname': None,
                        'snmp_version': 2,
                        'ip_devices': ['localhost']
                    }
                ]
            },
            'pattoo-agent-os-spoked': {
                'listen_address': '127.0.0.1',
                'ip_bind_port': 5000
                },
            'pattoo-agent-os-hubd': {

                'ip_devices': [
                    {'ip_address': '127.0.0.1',
                     'ip_bind_port': 5000}]
                }
        }

    def create(self):
        """Create a good config and set the PATTOO_CONFIGDIR variable.

        Args:
            None

        Returns:
            self.config_directory: Directory where the config is placed

        """
        # Initialize key variables
        config_file = '{}/unittest_config.yaml'.format(self._config_directory)

        # Write good_config to file
        with open(config_file, 'w') as f_handle:
            yaml.dump(self._config, f_handle, default_flow_style=False)

        # Return
        return self._config_directory

    def cleanup(self):
        """Remove all residual directories.

        Args:
            None

        Returns:
            None

        """
        # Delete directories
        directories = [
            self._log_directory,
            self._cache_directory,
            self._daemon_directory,
            self._config_directory]
        for directory in directories:
            _delete_files(directory)


def _delete_files(directory):
    """Delete all files in directory."""
    # Cleanup files in temp directories
    filenames = [filename for filename in os.listdir(
        directory) if os.path.isfile(
            os.path.join(directory, filename))]

    # Get the full filepath for the cache file and remove filepath
    for filename in filenames:
        filepath = os.path.join(directory, filename)
        os.remove(filepath)

    # Remove directory after files are deleted.
    os.rmdir(directory)


def _environment():
    """Make sure environmental variables are OK.

    Args:
        None

    Returns:
        None

    """
    # Create a message for the screen
    screen_message = ('''
The PATTOO_CONFIGDIR is set to the wrong directory. Run this command to do \
so:

$ export PATTOO_CONFIGDIR={}

Then run this command again, followed by.

$ ./_do_all_tests.py
'''.format(CONFIG_DIRECTORY))

    # Make sure the PATTOO_CONFIGDIR environment variable is set
    if 'PATTOO_CONFIGDIR' not in os.environ:
        log.log2die_safe(1023, screen_message)

    # Make sure the PATTOO_CONFIGDIR environment variable is set correctly
    if os.environ['PATTOO_CONFIGDIR'] != CONFIG_DIRECTORY:
        log.log2die_safe(1024, screen_message)

    # Make sure the PATTOO_CONFIGDIR environment variable is set to unittest
    if 'unittest' not in os.environ['PATTOO_CONFIGDIR']:
        log_message = (
            'The PATTOO_CONFIGDIR is not set to a unittest directory')
        log.log2die_safe(1025, log_message)


def ready():
    """Verify that we are ready to run tests."""
    # Check environment
    _environment()

    # Create configuration
    config = TestConfig()
    _ = config.create()


def main():
    """Verify that we are ready to run tests."""
    # Check environment
    _environment()

    # Check environment
    config = TestConfig()
    _ = config.create()


if __name__ == '__main__':
    # Do the unit test
    main()
