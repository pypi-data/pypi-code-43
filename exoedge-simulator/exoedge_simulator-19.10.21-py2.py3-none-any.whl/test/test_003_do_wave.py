import unittest
import time
from .simulator_test import SimulatorTest

class TestSinWave(SimulatorTest):

    def test_003_do_wave(self):
        time.sleep(2.0)
        num_samples = 0
        print('*'*8+"THE LIST"+'*'*8)
        print(list(self.test_q.queue))
        for i in list(self.test_q.queue):
            print("checking: {}".format(i))
            if i.get('data_in'):
                num_samples += 1
        self.assertGreater(num_samples, 8)

def main():
    unittest.main()

if __name__ == "__main__":
    main()
