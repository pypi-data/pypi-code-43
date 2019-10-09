import numpy as np


def generate_swiss_roll(oscilations, a, n):
    mean1 = [0.3, 0.3]
    mean2 = [0.3, 0.7]
    mean3 = [0.7, 0.3]
    mean4 = [0.7, 0.7]
    cov = [[0.01, 0], [0, 0.01]]

    x1 = np.random.multivariate_normal(mean1, cov, n)
    x2 = np.random.multivariate_normal(mean2, cov, n)
    x3 = np.random.multivariate_normal(mean3, cov, n)
    x4 = np.random.multivariate_normal(mean4, cov, n)
    xx = np.concatenate((x1, x2, x3, x4), axis=0)

    labels = [0] * n + [1] * n + [2] * n + [3] * n

    X = np.zeros((xx.shape[0], 3))
    for i in range(X.shape[0]):
        x, y = xx[i, 0], xx[i, 1]
        X[i, 0] = x * np.cos(oscilations * x)
        X[i, 1] = a * y
        X[i, 2] = x * np.sin(oscilations * x)

    return X, labels
