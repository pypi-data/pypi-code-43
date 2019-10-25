import numpy as np
from scipy import stats

import pytest
import numpy.testing as npt

from ..statistics import fit_binomial


def test_binomial():
    # generate data
    n = 10
    p_true = .3

    np.random.seed(42)
    data = stats.binom.rvs(n, p_true, size=8)

    # fit
    p_mle = fit_binomial(n, data)

    # check results
    npt.assert_almost_equal(p_mle, p_true)
