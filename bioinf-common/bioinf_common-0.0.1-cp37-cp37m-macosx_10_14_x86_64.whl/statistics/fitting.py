from typing import List

import numpy as np

from scipy import stats, optimize


def fit_binomial(n: float, k_list: List[float]) -> float:
    """Compute MLE for probability `p`."""
    def loglikelihood(p, *args):
        n, k_list = args
        return np.sum([stats.binom.logpmf(k, n, p) for k in k_list])

    fit = optimize.minimize(
        lambda p, *args: -loglikelihood(p, *args),
        x0=0.5, args=(n, k_list),
        method='Nelder-Mead')
    assert fit.success, 'Fit failed'

    return fit.x
