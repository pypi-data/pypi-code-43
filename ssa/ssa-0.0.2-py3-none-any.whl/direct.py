import numba as nb
import numpy as np

from .util import sample_discrete
from .output import Output


#@nb.jit
def direct(
        reactants: np.ndarray,
        reaction_matrix: np.ndarray,
        x0: np.ndarray,
        k: np.ndarray,
        t_max: np.ndarray,
        output: Output):
    # prepared running variables
    t = 0.0
    x = x0.copy()

    # prepare output and append initial state
    output.initialize(t, x, t_max)

    # reaction counter
    n_reaction = 0

    while t < t_max:
        # find reaction hazards
        hazards = k * (x ** reactants).prod(axis=1)

        # cumulative distribution
        cdv = np.cumsum(hazards)
        # total hazard
        h0 = cdv[-1]

        # sample exponential time
        if h0 == 0.0:
            # no more reactions
            break

        delta_t = - 1.0 / h0 * np.log(np.random.uniform())

        # sample reaction index
        cdv /= h0
        index = sample_discrete(cdv)

        # update state
        t = t + delta_t
        x = x + reaction_matrix[index]

        # append to output
        output.append(t, x)

        n_reaction += 1

    # fill possibly remaining fields
    output.finalize()

    # print("Number of reactions: ", n_reaction)

    # transform to ndarrays
    ts, xs = output.as_ndarrays()

    return ts, xs
