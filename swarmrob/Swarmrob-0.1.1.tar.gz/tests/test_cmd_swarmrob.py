#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from unittest.mock import patch
from swarmrob import swarmrob

from swarmrob.utils import pyro_interface


class TestCmdSwarmrobSwitchCommand(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_daemon(self):
        try:
            self.assertFalse(swarmrob.switch_command('daemon'))
        except KeyError:
            self.fail(msg="The master init command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_master(self):
        try:
            self.assertFalse(swarmrob.switch_command('master'))
        except KeyError:
            self.fail(msg="The master swarm_status command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_worker(self):
        try:
            self.assertFalse(swarmrob.switch_command('worker'))
        except KeyError:
            self.fail(msg="The master worker_status command does not exist")

    @patch('sys.argv', ['-i', 'lo', '-r', 'foo'])
    def test_switch_command_check(self):
        try:
            self.assertFalse(swarmrob.switch_command('check'))
        except KeyError:
            self.fail(msg="The master start_swarm command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_help(self):
        try:
            self.assertTrue(swarmrob.switch_command('help'))
        except KeyError:
            self.fail(msg="The master help command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_non_existent(self):
        try:
            swarmrob.switch_command('non_existent')
            self.fail(msg="An unknown command should throw a KeyError")
        except KeyError:
            pass


class TestCmdSwarmrobCheckForStartup(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-r', 'foo'])
    def test_check_for_startup(self):
        self.assertTrue(swarmrob.check_for_startup())

    @patch('sys.argv', ['-r', 'non_existent'])
    def test_check_for_startup_non_existent_repo(self):
        self.assertFalse(swarmrob.check_for_startup())


class TestCmdSwarmrobShowHelp(TestCase):
    def test_show_help(self):
        self.assertTrue(swarmrob.show_help())


class TestCmdSwarmrobPrintMasterErrorMessage(TestCase):
    def test_print_master_error_message(self):
        self.assertTrue(swarmrob.print_master_error_message())


class TestCmdSwarmrobIsMasterAvailable(TestCase):
    def test_is_master_available(self):
        self.assertTrue(swarmrob.is_master_available())


def reset_daemon_dummy():
    swarmrob_daemon_proxy = pyro_interface.get_daemon_proxy("127.0.0.1")
    swarmrob_daemon_proxy.reset_dummy()
