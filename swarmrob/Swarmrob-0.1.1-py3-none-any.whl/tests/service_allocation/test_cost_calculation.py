import queue
import jsonpickle
from unittest import TestCase

from daemon_dummy import worker_dummy
from swarmrob.service_allocation import cost_calculation
from swarmrob.services import service
from swarmrob.logger import evaluation_logger


class WorkerDummy:
    def __init__(self, tag="", val=100):
        self.val = val
        self.tag = tag
        self.hostname = "foo"
        self.uuid = "bar"
        self.advertise_address = "127.0.0.1"

    def get_cpu_usage(self):
        return self.val

    def get_vram_usage(self):
        return self.val

    def get_swap_ram_usage(self):
        return self.val

    def get_remaining_image_download_size(self, image_tag):
        if self.tag == image_tag:
            return self.val
        return 0

    def get_bandwidth(self, repository):
        if repository is None:
            return self.val
        return 0

    def check_hardware(self, srv):
        if self.tag == jsonpickle.decode(srv).tag:
            return 1
        return 0


class TestCostCalculationInit(TestCase):
    def setUp(self):
        self.cost_calculation = default_setup()

    def test___init__(self):
        self.assertIsNotNone(self.cost_calculation.cpu_cost_weight)
        self.assertIsNotNone(self.cost_calculation.vram_cost_weight)
        self.assertIsNotNone(self.cost_calculation.swap_cost_weight)
        self.assertIsNotNone(self.cost_calculation.image_download_cost_weight)


class TestCostCalculationFunction(TestCase):
    def setUp(self):
        self.cost_calculation = default_setup()

    def test_cost_calculation(self):
        srv = service.Service("foo", "bar")
        worker = WorkerDummy("bar")
        q = queue.Queue()
        self.cost_calculation.calculate_costs_and_check_hardware_in_thread(0, srv, worker, q)
        self.assertEqual({0: {'cost': 99999, 'hw': 1}}, q.get())

    def test_cost_calculation_params_none(self):
        self.assertIsNone(self.cost_calculation.calculate_costs_and_check_hardware_in_thread(None, None, None, None))

    def test_cost_calculation_2(self):
        srv = service.Service("foo", "bar")
        worker = WorkerDummy("bar", 0)
        q = queue.Queue()
        self.cost_calculation.calculate_costs_and_check_hardware_in_thread(0, srv, worker, q)
        self.assertEqual({0: {'cost': 25000, 'hw': 1}}, q.get())

    def test_cost_calculation_3(self):
        srv = service.Service("foo", "foo:bar")
        worker = WorkerDummy("", 100)
        q = queue.Queue()
        self.cost_calculation.calculate_costs_and_check_hardware_in_thread(0, srv, worker, q)
        self.assertEqual({0: {'cost': 100000, 'hw': 0}}, q.get())

    def test_cost_calculation_4(self):
        srv = service.Service("foo", "foo:bar")
        worker = WorkerDummy("foo:bar", 50)
        q = queue.Queue()
        self.cost_calculation.calculate_costs_and_check_hardware_in_thread(0, srv, worker, q)
        self.assertEqual({0: {'cost': 40625, 'hw': 1}}, q.get())

    def test_cost_calculation_5(self):
        srv = service.Service("foo", "foo:bar")
        worker = WorkerDummy("foo:baz", 50)
        q = queue.Queue()
        self.cost_calculation.calculate_costs_and_check_hardware_in_thread(0, srv, worker, q)
        self.assertEqual({0: {'cost': 40625, 'hw': 0}}, q.get())


class TestCostCalculationCalculateOverallCosts(TestCase):
    def setUp(self):
        self.cost_calculation = default_setup()

    def test_calculate_overall_costs(self):
        self.assertEqual(1, self.cost_calculation._calculate_overall_costs(1, 1, 1, 1))

    def test_calculate_overall_costs_only_cpu_costs(self):
        self.assertEqual(0.25, self.cost_calculation._calculate_overall_costs(1, 0, 0, 0))

    def test_calculate_overall_costs_only_vram_costs(self):
        self.assertEqual(0.25, self.cost_calculation._calculate_overall_costs(0, 1, 0, 0))

    def test_calculate_overall_costs_only_swap_costs(self):
        self.assertEqual(0.25, self.cost_calculation._calculate_overall_costs(0, 0, 1, 0))

    def test_calculate_overall_costs_only_image_download_costs(self):
        self.assertEqual(0.25, self.cost_calculation._calculate_overall_costs(0, 0, 0, 1))


class TestCostCalculationCalculatePartialCosts(TestCase):
    def setUp(self):
        self.cost_calculation = default_setup()

    def test_calculate_partial_costs(self):
        cpu_costs, vram_costs, swap_costs, image_download_costs = self.cost_calculation._calculate_partial_costs(
            1, 1, 1, 1, 1
        )
        self.assertEqual(100000, cpu_costs)
        self.assertEqual(100000, vram_costs)
        self.assertEqual(100000, swap_costs)
        self.assertEqual(0, image_download_costs)

    def test_calculate_partial_costs_all_zero(self):
        cpu_costs, vram_costs, swap_costs, image_download_costs = self.cost_calculation._calculate_partial_costs(
            0, 0, 0, 0, 0
        )
        self.assertEqual(0, cpu_costs)
        self.assertEqual(0, vram_costs)
        self.assertEqual(0, swap_costs)
        self.assertEqual(100000, image_download_costs)


class TestGetUsageOfWorker(TestCase):
    def setUp(self):
        self.cost_calculation = default_setup()

    def test_get_usage_of_worker(self):
        worker = worker_dummy.Worker("foo", "lo", "bar")
        srv = service.Service("baz", "hello-world")
        cpu_usage, vram_usage, swap_usage, image_size, bandwidth_percent = self.cost_calculation._get_usage_of_worker(
            worker, srv)
        self.assertEqual(0.005, cpu_usage)
        self.assertEqual(0.005, vram_usage)
        self.assertEqual(0.005, swap_usage)
        self.assertEqual(100, image_size)
        self.assertEqual(8e-06, bandwidth_percent)


def default_setup():
    evaluation_logger.EvaluationLogger().enable(False)
    return cost_calculation.CostCalculation()
