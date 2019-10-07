from unittest import TestCase

from swarmrob.swarmengine import mode


class TestMode(TestCase):
    def test_not_defined(self):
        self.assertEqual("NONE", mode.Mode.NOT_DEFINED.value)

    def test_worker(self):
        self.assertEqual("WORKER", mode.Mode.WORKER.value)

    def test_master(self):
        self.assertEqual("MASTER", mode.Mode.MASTER.value)
