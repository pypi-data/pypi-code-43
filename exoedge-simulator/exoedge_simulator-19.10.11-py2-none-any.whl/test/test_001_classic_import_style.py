import unittest
import time
from .simulator_test import SimulatorTest

class TestSinWave(SimulatorTest):

    def test_005_classic_import_style(self):
        time.sleep(0.5)
        num_samples = 0
        for i in list(self.test_q.queue):
            print("checking: {}".format(i))
            if i.get('data_in'):
                num_samples += 1
        self.assertGreater(num_samples, 0)
        self.test_q.queue.clear()
        time.sleep(0.5)
        num_samples = 0
        for i in list(self.test_q.queue):
            print("checking: {}".format(i))
            if i.get('data_in'):
                num_samples += 1
        self.assertGreater(num_samples, 0)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
