import numpy as np


class LogisticFunction:
    """
    https://en.wikipedia.org/wiki/Logistic_function
    """
    def __init__(self, x_0=0, K=1, L=1):
        self.x_0 = x_0
        self.K = K
        self.L = L

    def __call__(self, x):
        return self.L / (1 + np.exp(-1 * self.K * (x - self.x_0)))


if __name__ == "__main__":
    lf = LogisticFunction()
    result = lf(np.array([-1, 1]))
    print(result)

    lf = LogisticFunction(K=9)
    result = lf(np.array([-1, 1]))
    print(result)

    lf = LogisticFunction(K=.09)
    result = lf(np.array([-1, 1]))
    print(result)

    lf = LogisticFunction(K=.09, x_0=50)
    result = lf(np.array(range(1, 101)))
    print(result)
