import unittest
from .simulator_test import SimulatorTest

class TestSinWave(SimulatorTest):

    @unittest.skip("need to find replacement for psutil")
    def test_006_architecture(self):
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
