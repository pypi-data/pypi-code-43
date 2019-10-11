import unittest
from .simulator_test import SimulatorTest

class TestSinWave(SimulatorTest):

    def test_001_sin_wave(self):
        self.assertIsNotNone(self.test_q.get(timeout=1.0))

def main():
    unittest.main()

if __name__ == "__main__":
    main()
