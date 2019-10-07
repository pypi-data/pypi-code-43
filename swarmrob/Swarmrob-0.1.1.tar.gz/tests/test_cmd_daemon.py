from unittest import TestCase
from unittest.mock import patch

from swarmrob import master, worker, daemon
from swarmrob.utils import pyro_interface


def fake_get_help(obj, num):
    return 'help'


def fake_get_non_existent(obj, num):
    return 'non_existent'


class TestCmdDaemonMain(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    @patch('clint.arguments.Args.get', fake_get_help)
    def test_main(self):
        try:
            self.assertTrue(daemon.main())
        except KeyError:
            self.fail(msg="daemon main should catch the KeyError")

    @patch('sys.argv', ['-i', 'lo'])
    @patch('clint.arguments.Args.get', fake_get_non_existent)
    def test_main_non_existent(self):
        try:
            self.assertFalse(daemon.main())
        except KeyError:
            self.fail(msg="daemon main should catch the KeyError")


# Not testing the start and stop commands because these would mess up other tests using the swarmrob daemon dummy


class TestCmdDaemonSwitchCommand(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_status(self):
        try:
            daemon.switch_command('status')
        except KeyError:
            self.fail(msg="The daemon status command does not exist")

    def test_switch_command_help(self):
        try:
            daemon.switch_command('help')
        except KeyError:
            self.fail(msg="The daemon help command does not exist")

    def test_switch_command_check(self):
        try:
            daemon.switch_command('check')
        except KeyError:
            self.fail(msg="The daemon check command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_non_existent(self):
        try:
            daemon.switch_command('non_existent')
            self.fail(msg="An unknown command should throw a KeyError")
        except KeyError:
            pass


class TestCmdDaemonShowHelp(TestCase):
    def test_show_help(self):
        self.assertTrue(daemon.show_help())


class TestCmdDaemonCheckDaemonRunning(TestCase):
    def test_check_daemon_running(self):
        self.assertTrue(daemon.check_daemon_running('lo'))

    def test_check_daemon_running_non_existent_interface(self):
        self.assertFalse(daemon.check_daemon_running('non_existent'))


class TestCmdDaemonStatusDaemon(TestCase):
    @patch('sys.argv', ['-i', 'lo'])
    def test_status_daemon(self):
        self.assertTrue(daemon.status_daemon())

    @patch('sys.argv', ['-i', 'non_existent'])
    def test_status_daemon_non_existent_interface(self):
        self.assertFalse(daemon.status_daemon())


class TestCmdDaemonCheckDocker(TestCase):
    def test_check_docker(self):
        self.assertTrue(daemon.check_docker())


def reset_daemon_dummy():
    swarmrob_daemon_proxy = pyro_interface.get_daemon_proxy("127.0.0.1")
    swarmrob_daemon_proxy.reset_dummy()
