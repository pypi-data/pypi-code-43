import unittest
from unittest import TestCase
from pollinghub import PollingHub, Pollee
import time
import threading
import logging


class TestPollingHub(TestCase):
    TEST_DATA = [
        {'test_time': 5, 'intervals': [1, 2], 'expected': [5, 2]},
        {'test_time': 5, 'intervals': [1, 2, 3], 'expected': [5, 2, 1]},
        {'test_time': 5, 'intervals': [3, 2, 1], 'expected': [1, 2, 5]},
        {'test_time': 5, 'intervals': [1, 3, 2], 'expected': [5, 1, 2]},
    ]

    def setUp(self):
        if not hasattr(self, 'log'):
            self.log = logging.getLogger(self.__class__.__name__)
        self.test_lock = threading.Lock()

    def tearDown(self):
        self.test_lock = None

    def _count(self, name):
        with self.test_lock:
            if name not in self.my_result:
                self.my_result[name] = 1
            else:
                self.my_result[name] += 1

    def test_polling_hub(self):
        for t in self.TEST_DATA:
            print("\n---")
            print("intervals: {}".format(t['intervals']))
            hub = PollingHub()

            # check test data itself
            self.assertEqual(len(t['intervals']), len(t['expected']))

            for i in range(len(t['intervals'])):
                name = 'p' + str(i)
                hub.reg(Pollee(name, t['intervals'][i], self._count, i))

            self.my_result = {}

            hub.start()
            time.sleep(t['test_time']+1)
            hub.stop()

            print("expected: {}".format(t['expected']))
            print("result: {}".format(self.my_result))

            for i in range(len(t['expected'])):
                self.assertTrue(self.my_result[i] >= t['expected'][i])

            # test multiple start/stop
            hub.start()
            time.sleep(t['test_time'] + 1)
            hub.stop()

            print("expected: {}".format(t['expected']))
            print("result: {}".format(self.my_result))

            for i in range(len(t['expected'])):
                self.assertTrue(self.my_result[i] >= t['expected'][i])

    def test_no_pollee(self):
        hub = PollingHub()
        hub.start()
        time.sleep(3)
        hub.stop()
        self.log.debug('wake_count: %s', hub.wake_count)
        self.assertEqual(hub.wake_count, 1)  # only 1 for start thread

        hub.start()
        time.sleep(3)
        hub.stop()
        self.log.debug('wake_count: %s', hub.wake_count)
        self.assertEqual(hub.wake_count, 1)  # only 1 for start thread

    def test_start_stop(self):
        hub = PollingHub()
        self.assertFalse(hub.stop())
        self.assertTrue(hub.start())
        self.assertFalse(hub.start())
        self.assertTrue(hub.stop())
        self.assertFalse(hub.stop())

        self.assertTrue(hub.start())
        self.assertTrue(hub.stop())

    def test_reg_unreg_pollee(self):
        hub = PollingHub()

        # test reg a invalid pollee
        self.assertFalse(hub.reg(123))

        p1 = Pollee('p1', 1, self._count, 'p1')
        p2 = Pollee('p2', 1, self._count, 'p2')

        # test reg again
        self.assertTrue(hub.reg(p1))
        self.assertFalse(hub.reg(p1))

        self.my_result = {}
        self.assertTrue(hub.start())

        # test reg when running
        self.assertTrue(hub.reg(p2))
        time.sleep(3)
        self.assertTrue('p1' in self.my_result)
        self.assertTrue('p2' in self.my_result)

        # test un_reg when running
        self.assertTrue(hub.un_reg(p1))
        self.my_result = {}
        time.sleep(3)
        self.assertFalse('p1' in self.my_result)

        # test reg again
        self.assertTrue(hub.reg(p1))
        self.my_result = {}
        time.sleep(3)
        self.assertTrue('p1' in self.my_result)

        self.assertTrue(hub.stop())

        # un_reg
        self.assertTrue(hub.un_reg(p2))


if __name__ == '__main__':
    LOG_FMT = "%(asctime)s [%(levelname)s] " \
              "%(filename)s:%(lineno)s %(name)s %(funcName)s() : %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=LOG_FMT)
    unittest.main()
