#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from unittest import TestCase
from unittest.mock import patch

from swarmrob import master, worker
from swarmrob.utils import pyro_interface


DIR = os.path.dirname(__file__)
COMPOSE_TEST = DIR + "/compose_test.yaml"


def fake_get_init(obj, num):
    return 'init'


def fake_get_non_existent(obj, num):
    return 'non_existent'


class TestCmdMasterMain(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    @patch('clint.arguments.Args.get', fake_get_init)
    def test_main(self):
        try:
            self.assertTrue(master.main())
        except KeyError:
            self.fail(msg="master main should catch the KeyError")

    @patch('sys.argv', ['-i', 'lo'])
    @patch('clint.arguments.Args.get', fake_get_non_existent)
    def test_main_non_existent(self):
        try:
            self.assertFalse(master.main())
        except KeyError:
            self.fail(msg="master main should catch the KeyError")


class TestCmdMasterSwitchCommand(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_init(self):
        try:
            master.switch_command('init')
        except KeyError:
            self.fail(msg="The master init command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_swarm_status(self):
        try:
            master.switch_command('swarm_status')
        except KeyError:
            self.fail(msg="The master swarm_status command does not exist")

    @patch('sys.argv', ['-i', 'lo', '-w', 'foo'])
    def test_switch_command_worker_status(self):
        try:
            master.switch_command('worker_status')
        except KeyError:
            self.fail(msg="The master worker_status command does not exist")

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo', '-c', '/foo/bar'])
    def test_switch_command_start_swarm(self):
        try:
            master.switch_command('start_swarm')
        except KeyError:
            self.fail(msg="The master start_swarm command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_help(self):
        try:
            master.switch_command('help')
        except KeyError:
            self.fail(msg="The master help command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_non_existent(self):
        try:
            master.switch_command('non_existent')
            self.fail(msg="An unknown command should throw a KeyError")
        except KeyError:
            pass


class TestCmdMasterInitswarm(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    def test_init_swarm(self):
        self.assertTrue(master.init_swarm())

    @patch('sys.argv', ['-i', 'lo', '-a', '127.0.0.1'])
    def test_init_swarm_advertise_address(self):
        self.assertTrue(master.init_swarm())

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo'])
    def test_init_swarm_uuid(self):
        self.assertTrue(master.init_swarm())

    @patch('sys.argv', ['--interface', 'lo'])
    def test_init_swarm_long_param(self):
        self.assertTrue(master.init_swarm())

    @patch('sys.argv', ['-i', 'lo', '--advertise_address', '127.0.0.1'])
    def test_init_swarm_long_param_advertise_address(self):
        self.assertTrue(master.init_swarm())

    @patch('sys.argv', ['-i', 'lo', '--uuid', 'foo'])
    def test_init_swarm_long_param_uuid(self):
        self.assertTrue(master.init_swarm())

    @patch('sys.argv', ['-i', 'non_existent'])
    def test_init_swarm_non_existent_interface(self):
        self.assertFalse(master.init_swarm())


class TestCmdMasterSwarmStatus(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    def test_swarm_status(self):
        master.init_swarm()
        self.assertTrue(master.swarm_status())

    @patch('sys.argv', ['--interface', 'lo'])
    def test_swarm_status_long_param(self):
        master.init_swarm()
        self.assertTrue(master.swarm_status())

    @patch('sys.argv', ['-i', 'non_existent'])
    def test_swarm_status_non_existent_interface(self):
        self.assertFalse(master.swarm_status())

    @patch('sys.argv', ['-i', 'lo'])
    def test_swarm_status_swarm_not_initialized(self):
        self.assertFalse(master.swarm_status())


class TestCmdMasterWorkerStatus(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo@127.0.0.1', '-w', 'bar'])
    def test_worker_status(self):
        master.init_swarm()
        worker.join_swarm()
        self.assertTrue(master.worker_status())

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo@127.0.0.1', '-w', 'bar'])
    def test_worker_status_no_worker_joined(self):
        master.init_swarm()
        self.assertFalse(master.worker_status())

    @patch('sys.argv', ['-i', 'non_existent', '-u', 'foo@127.0.0.1', '-w', 'bar'])
    def test_worker_status_non_existent_interface(self):
        self.assertFalse(master.worker_status())


class TestCmdMasterStartSwarmByComposeFile(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo', '-c', COMPOSE_TEST])
    def test_start_swarm_by_compose_file(self):
        master.init_swarm()
        self.assertTrue(master.start_swarm_by_compose_file())

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo', '-c', COMPOSE_TEST])
    def test_start_swarm_by_compose_file_no_swarm_initialized(self):
        self.assertFalse(master.start_swarm_by_compose_file())

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo', '-c', 'non_existent'])
    def test_start_swarm_by_compose_file_non_existent_compose_file(self):
        master.init_swarm()
        self.assertFalse(master.start_swarm_by_compose_file())

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo', '-c', COMPOSE_TEST, '-l', 'baz', '-f', '/tmp'])
    def test_start_swarm_by_compose_file_logger_params(self):
        master.init_swarm()
        self.assertTrue(master.start_swarm_by_compose_file())

    @patch('sys.argv', ['--interface', 'lo', '--uuid', 'foo', '--compose_file', COMPOSE_TEST,
                        '--log_identifier', 'baz', '--log_folder', '/tmp'])
    def test_start_swarm_by_compose_file_long_params(self):
        master.init_swarm()
        self.assertTrue(master.start_swarm_by_compose_file())

    @patch('sys.argv', ['-i', 'non_existent', '-u', 'foo', '-c', COMPOSE_TEST])
    def test_start_swarm_by_compose_file_non_existent_interface(self):
        self.assertFalse(master.start_swarm_by_compose_file())


def reset_daemon_dummy():
    swarmrob_daemon_proxy = pyro_interface.get_daemon_proxy("127.0.0.1")
    swarmrob_daemon_proxy.reset_dummy()
