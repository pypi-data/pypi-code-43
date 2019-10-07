from unittest import TestCase
from swarmrob.swarmengine import swarm, swarm_engine_master, swarm_engine_worker


class TestSwarmInit(TestCase):
    def setUp(self):
        self.master, self.worker, self.swarm = default_setup()

    def test___init__(self):
        self.assertEqual("foo", self.swarm.uuid)
        self.assertEqual(self.master.advertise_address, self.swarm.advertise_address)
        self.assertEqual(dict(), self.swarm._worker_list)
        self.assertEqual(self.master, self.swarm._master)
        self.assertEqual("foo", self.swarm._master.swarm_uuid)

    def test___init__none_uuid(self):
        test_swarm = swarm.Swarm(None, self.master)
        self.assertIsNotNone(test_swarm.uuid)
        self.assertEqual(self.master.advertise_address, test_swarm.advertise_address)
        self.assertEqual(dict(), test_swarm._worker_list)
        self.assertEqual(self.master, test_swarm._master)
        self.assertEqual(test_swarm.uuid, test_swarm._master.swarm_uuid)

    def test___init__none_master(self):
        test_swarm = swarm.Swarm("foo", None)
        self.assertEqual("foo", test_swarm.uuid)
        self.assertIsNone(test_swarm.advertise_address)
        self.assertEqual(dict(), test_swarm._worker_list)
        self.assertIsNone(test_swarm._master)


class TestSwarmAddWorkerToList(TestCase):
    def setUp(self):
        self.master, self.worker, self.swarm = default_setup()

    def test_add_worker_to_list(self):
        self.swarm.add_worker_to_list(self.worker)
        self.assertEqual({str(self.worker.uuid): self.worker}, self.swarm._worker_list)

    def test_add_worker_to_list_none(self):
        self.swarm.add_worker_to_list(None)
        self.assertEqual({}, self.swarm._worker_list)


class TestSwarmRemoveWorkerFromList(TestCase):
    def setUp(self):
        self.master, self.worker, self.swarm = default_setup()

    def test_remove_worker_from_list(self):
        self.swarm.add_worker_to_list(self.worker)
        self.swarm.remove_worker_from_list(self.worker.uuid)
        self.assertEqual({}, self.swarm._worker_list)

    def test_remove_worker_from_list_none(self):
        self.swarm.add_worker_to_list(self.worker)
        self.swarm.remove_worker_from_list(None)
        self.assertEqual({str(self.worker.uuid): self.worker}, self.swarm._worker_list)


class TestSwarmGetWorker(TestCase):
    def setUp(self):
        self.master, self.worker, self.swarm = default_setup()

    def test_get_worker(self):
        self.swarm.add_worker_to_list(self.worker)
        self.assertEqual(self.worker, self.swarm.get_worker(self.worker.uuid))

    def test_get_worker_none(self):
        self.swarm.add_worker_to_list(self.worker)
        self.assertIsNone(self.swarm.get_worker(None))


class TestSwarmGetWorkerCount(TestCase):
    def setUp(self):
        self.master, self.worker, self.swarm = default_setup()

    def test_get_worker_count(self):
        self.swarm.add_worker_to_list(self.worker)
        self.swarm.add_worker_to_list(swarm_engine_worker.Worker("bar", "lo"))
        self.swarm.add_worker_to_list(swarm_engine_worker.Worker("baz", "lo"))
        self.assertEqual(3, self.swarm.get_worker_count())

    def test_get_worker_count_empty(self):
        self.assertEqual(0, self.swarm.get_worker_count())

    def test_get_worker_count_one(self):
        self.swarm.add_worker_to_list(self.worker)
        self.assertEqual(1, self.swarm.get_worker_count())

    def test_get_worker_count_added_same_twice(self):
        self.swarm.add_worker_to_list(self.worker)
        self.swarm.add_worker_to_list(self.worker)
        self.assertEqual(1, self.swarm.get_worker_count())


class TestSwarmHasWorkerWithName(TestCase):
    def setUp(self):
        self.master, self.worker, self.swarm = default_setup()

    def test_has_worker_with_name(self):
        self.swarm.add_worker_to_list(self.worker)
        self.assertTrue(self.swarm.has_worker_with_name("foobar"))

    def test_has_worker_with_name_none(self):
        self.swarm.add_worker_to_list(self.worker)
        self.assertFalse(self.swarm.has_worker_with_name(None))

    def test_has_worker_with_name_empty(self):
        self.swarm.add_worker_to_list(self.worker)
        self.assertFalse(self.swarm.has_worker_with_name(""))


class TestSwarmGetUniqueWorkerHostname(TestCase):
    def setUp(self):
        self.master, self.worker, self.swarm = default_setup()

    def test_get_unique_worker_hostname(self):
        self.assertEqual("foobar", self.swarm.get_unique_worker_hostname("foobar"))

    def test_get_unique_worker_hostname_name_exists(self):
        self.swarm.add_worker_to_list(self.worker)
        self.assertEqual("foobar_1", self.swarm.get_unique_worker_hostname("foobar"))

    def test_get_unique_worker_hostname_name_exists_twice(self):
        self.swarm.add_worker_to_list(self.worker)
        worker2 = swarm_engine_worker.Worker("foo", "lo")
        worker2.hostname = "foobar_1"
        self.swarm.add_worker_to_list(worker2)
        self.assertEqual("foobar_2", self.swarm.get_unique_worker_hostname("foobar"))

    def test_get_unique_worker_hostname_hostname_none(self):
        self.assertEqual(None, self.swarm.get_unique_worker_hostname(None))


def default_setup():
    master = swarm_engine_master.Master("lo", "127.0.0.1")
    worker = swarm_engine_worker.Worker("foo", "lo")
    worker.hostname = "foobar"
    sw = swarm.Swarm("foo", master)
    return master, worker, sw
