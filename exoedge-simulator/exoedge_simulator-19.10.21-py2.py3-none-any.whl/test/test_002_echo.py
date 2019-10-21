import unittest
import json
from .simulator_test import SimulatorTest

class TestSinWave(SimulatorTest):

    def test_002_echo(self):
        print("throwing away config_io from queue: {}".format(self.test_q.get(timeout=0.5)))
        data_in = self.test_q.get(timeout=1.0)['data_in']
        data_in_values = list(data_in.values())
        self.assertEqual(json.loads(data_in_values[-1])['one'], "there is no spoon")

def main():
    unittest.main()

if __name__ == "__main__":
    main()
