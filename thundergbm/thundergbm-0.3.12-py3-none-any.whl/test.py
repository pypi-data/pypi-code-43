from thundergbm import TGBMRegressor
from sklearn.datasets import load_boston
from sklearn.metrics import mean_squared_error
from multiprocessing.pool import ThreadPool as Pool
import functools
import numpy as np


def main():
    print("Without parallel threads: " + str(calc(2, 1)))
    print("With parallel threads: " + str(calc(2, 2)))

def calc(num_repeats, pool_size):
    x, y = load_boston(return_X_y=True)
    x = np.repeat(x, 1000, axis=0)
    y = np.repeat(y, 1000)

    x = np.asarray([x]*num_repeats)
    y = np.asarray([y]*num_repeats)

    pool = Pool(pool_size)
    func = functools.partial(fit_gbdt, x=x, y=y)
    results = pool.map(func, range(num_repeats))
    return results

def fit_gbdt(idx, x, y):
    clf = TGBMRegressor(verbose=0)
    clf.fit(x[idx], y[idx])
    y_pred = clf.predict(x[idx])
    rmse = (mean_squared_error(y[idx], y_pred)**(1/2))
    return rmse

if __name__ == '__main__':
    main()
