import unittest
from pollinghub import PollingHub, Pollee
import time
import threading


class TestPollingHub(unittest.TestCase):
    TEST_DATA = [
        {'test_time': 5, 'intervals': [1, 2], 'expected': [5, 2]},
        {'test_time': 5, 'intervals': [1, 2, 3], 'expected': [5, 2, 1]},
        {'test_time': 5, 'intervals': [3, 2, 1], 'expected': [1, 2, 5]},
        {'test_time': 5, 'intervals': [1, 3, 2], 'expected': [5, 1, 2]},
    ]

    def setUp(self):
        self.test_lock = threading.Lock()

    def tearDown(self):
        self.test_lock = None

    def count(self, name):
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
                hub.reg(Pollee(name, t['intervals'][i], self.count, i))

            self.my_result = {}

            hub.start()
            time.sleep(t['test_time']+1)
            hub.stop()

            print("expected: {}".format(t['expected']))
            print("result: {}".format(self.my_result))

            for i in range(len(t['expected'])):
                self.assertTrue(self.my_result[i] >= t['expected'][i])


if __name__ == '__main__':
    unittest.main()
