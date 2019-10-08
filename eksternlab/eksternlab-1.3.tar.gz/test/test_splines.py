import unittest
import numpy as np
from eksternlab import height, slope, curvature


SHOW = False


class TestSplines(unittest.TestCase):
    def test_interpolate(self):
        x = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        y = x**2
        h = height(x, y)
        y_interp = h(x)
        self.assertTrue(np.allclose(y, y_interp))

        if SHOW:
            from matplotlib import pyplot as plt
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(x, y, 'x')
            x = np.linspace(-0.1, 1.1, 100)
            ax.plot(x, h(x))
            plt.show()

    def test_slope(self):
        x = np.array([-0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
        y = x**2
        h = height(x, y)
        y_interp = h(x)

        x_interp = np.linspace(0.2, 0.8, 100)
        dydx = 2*x_interp
        angle = -np.arctan(dydx)
        s = slope(h, x_interp)

        if SHOW:
            from matplotlib import pyplot as plt
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(x_interp, angle, 'x')
            ax.plot(x_interp, s)
            plt.show()
        self.assertTrue(np.allclose(s, angle, atol=0.01))

    def test_curvature(self):
        x = np.array([-0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
        y = x**2
        h = height(x, y)
        x_interp = np.linspace(0.2, 0.8, 100)
        dydx = 2*x_interp
        dy2dx2 = 2
        kappa = dy2dx2/(1 + dydx**2)**(1.5)
        kappa_interp = curvature(h, x_interp)

        if SHOW:
            from matplotlib import pyplot as plt
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(x_interp, kappa, 'x')
            ax.plot(x_interp, kappa_interp)
            plt.show()

        self.assertTrue(np.allclose(kappa, kappa_interp, atol=0.2))


if __name__ == '__main__':
    unittest.main()