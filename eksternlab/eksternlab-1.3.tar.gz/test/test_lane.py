import unittest
import numpy as np
from eksternlab import Lane
from eksternlab import extend_dataset


class TestLane(unittest.TestCase):
    def test_perfect_circle(self):
        t = np.linspace(0.1, np.pi/2.0-0.1, 500)
        x = -0.5 + np.sin(t)
        y = np.cos(t)

        lane = Lane(x, y)
        h = lane.height(smooth=5)
        self.assertTrue(np.allclose(h(x), y, atol=0.1))

        angle = lane.slope(smooth=5)
        expect = t
        self.assertTrue(np.allclose(expect, angle(x), atol=0.1))

        radius = lane.radius_of_curvature(smooth=5)
        self.assertTrue(np.allclose(radius(x)[10:-10], -1.0, atol=0.1))

    def test_extend_dataset(self):
        x = np.linspace(0.0, 2.0, 100)
        y = 2*x

        x_new, y_new = extend_dataset(x, y, -1.0, 4.0, num_points=10)
        self.assertAlmostEqual(x_new[0], -1.0)
        self.assertAlmostEqual(x_new[-1], 4.0)
        self.assertAlmostEqual(y_new[0], 2*x_new[0])
        self.assertAlmostEqual(y_new[-1], 2*x_new[-1])


if __name__ == '__main__':
    unittest.main()
