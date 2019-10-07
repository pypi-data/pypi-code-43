from unittest import TestCase
from unittest.mock import patch

from swarmrob import master, worker
from swarmrob.utils import pyro_interface


def fake_get_status(obj, num):
    return 'status'


def fake_get_non_existent(obj, num):
    return 'non_existent'


class TestCmdWorkerMain(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    @patch('clint.arguments.Args.get', fake_get_status)
    def test_main(self):
        try:
            self.assertTrue(worker.main())
        except KeyError:
            self.fail(msg="worker main should catch the KeyError")

    @patch('sys.argv', ['-i', 'lo'])
    @patch('clint.arguments.Args.get', fake_get_non_existent)
    def test_main_non_existent(self):
        try:
            self.assertFalse(worker.main())
        except KeyError:
            self.fail(msg="worker main should catch the KeyError")


class TestCmdWorkerSwitchCommand(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo@127.0.0.1'])
    def test_switch_command_join(self):
        try:
            master.init_swarm()
            worker.switch_command('join')
        except KeyError:
            self.fail(msg="The worker join command does not exist")

    @patch('sys.argv', ['-i', 'lo', '-s', 'foo@127.0.0.1', '-w', 'bar'])
    def test_switch_command_leave(self):
        try:
            worker.switch_command('leave')
        except KeyError:
            self.fail(msg="The worker leave command does not exist")

    @patch('sys.argv', ['-i', 'lo', '-s', 'foo@127.0.0.1', '-u', 'bar'])
    def test_switch_command_status(self):
        try:
            worker.switch_command('status')
        except KeyError:
            self.fail(msg="The worker status command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_help(self):
        try:
            worker.switch_command('help')
        except KeyError:
            self.fail(msg="The worker help command does not exist")

    @patch('sys.argv', ['-i', 'lo'])
    def test_switch_command_non_existent(self):
        try:
            worker.switch_command('non_existent')
            self.fail(msg="An unknown command should throw a KeyError")
        except KeyError:
            pass


class TestCmdWorkerJoinSwarm(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo@127.0.0.1'])
    def test_join_swarm(self):
        master.init_swarm()
        self.assertTrue(worker.join_swarm())

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo@127.0.0.1'])
    def test_join_swarm_no_master_init(self):
        self.assertFalse(worker.join_swarm())

    @patch('sys.argv', ['-i', 'lo', '-u', 'foo@127.0.0.1', '-w', 'bar'])
    def test_join_swarm_worker_uuid(self):
        master.init_swarm()
        self.assertTrue(worker.join_swarm())

    @patch('sys.argv', ['-i', 'non_existent', '-u', 'foo@127.0.0.1'])
    def test_join_swarm_non_existent_interface(self):
        self.assertFalse(worker.join_swarm())


class TestCmdWorkerLeaveSwarm(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo', '-s', 'foo@127.0.0.1', '-u', 'foo@127.0.0.1', '-w', 'bar'])
    def test_leave_swarm(self):
        master.init_swarm()
        worker.join_swarm()
        self.assertTrue(worker.leave_swarm())

    @patch('sys.argv', ['-i', 'lo', '-s', 'foo@127.0.0.1', '-u', 'foo@127.0.0.1', '-w', 'bar'])
    def test_leave_swarm_no_worker_joined(self):
        master.init_swarm()
        self.assertFalse(worker.leave_swarm())

    @patch('sys.argv', ['-i', 'lo', '-s', 'baz@127.0.0.1', '-u', 'foo@127.0.0.1', '-w', 'bar'])
    def test_leave_swarm_wrong_swarm_uuid(self):
        master.init_swarm()
        worker.join_swarm()
        self.assertFalse(worker.leave_swarm())

    @patch('sys.argv', ['-i', 'non_existent', '-s', 'foo@127.0.0.1', '-u', 'foo@127.0.0.1', '-w', 'bar'])
    def test_leave_swarm_non_existent_interface(self):
        self.assertFalse(worker.leave_swarm())


class TestCmdWorkerStatusWorker(TestCase):
    def setUp(self):
        reset_daemon_dummy()

    @patch('sys.argv', ['-i', 'lo'])
    def test_status_worker(self):
        self.assertTrue(worker.status_worker())

    @patch('sys.argv', ['-i', 'non_existent'])
    def test_status_worker_non_existent_interface(self):
        self.assertFalse(worker.status_worker())


def reset_daemon_dummy():
    swarmrob_daemon_proxy = pyro_interface.get_daemon_proxy("127.0.0.1")
    swarmrob_daemon_proxy.reset_dummy()
