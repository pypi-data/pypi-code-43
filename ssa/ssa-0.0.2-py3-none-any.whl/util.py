import numba as nb
import numpy as np


# Avogadro's constant, [mol**(-1)]
NA = 6.02214085774e23

MSG_REACTION_ORDER = \
    "Generation of stochastic reaction coefficient constants from " \
    "reaction of order > 2 currently not supported. Consider rewriting " \
    "in terms of simpler reactions."


def k_det_to_k_stoch(
        k_det: np.ndarray,
        reactants: np.ndarray,
        volume: float = 1.0,
        use_na: bool = True):
    nr = reactants.shape[0]

    reaction_orders = np.sum(reactants, axis=1)
    if reaction_orders.max() > 2:
        raise ValueError(MSG_REACTION_ORDER)

    k_stoch = k_det.copy()
    
    if use_na:
        factor = NA * volume
    else:
        factor = 1.0 * volume
    print(reaction_orders)
    for ir in range(nr):
        print(reactants[ir, :])
        k_stoch[ir] /= np.power(factor, reaction_orders[ir] - 1)
        if np.max(reactants[ir, :]) == 2:
            k_stoch[ir] *= 2

    return k_stoch


def k_stoch_to_k_det(
        k_stoch: np.ndarray,
        reactants: np.ndarray,
        volume: float = 1.0,
        use_na: bool = True):
    nr = reactants.shape[0]

    reaction_orders = np.sum(reactants, axis=1)
    if reaction_orders.max() > 2:
        raise ValueError(MSG_REACTION_ORDER)

    k_det = k_stoch.copy()

    if use_na:
        factor = NA * volume
    else:
        factor = 1.0 * volume

    for ir in range(nr):
        k_det[ir] *= np.power(factor, reaction_orders[ir] - 1)
        if np.max(reactants[ir, :]) == 2:
            k_stoch[ir] /= 2

    return k_det


def molar_concentration_to_molecule_number(x, volume: float = 1.0, use_na=True):
    factor = NA if use_na else 1.0
    return factor * x * volume


def molecule_number_to_molar_concentration(x, volume: float = 1.0):
    factor = NA if use_na else 1.0
    return x / (factor * volume)


#@nb.jit
def sample_discrete(cdv):
    """
    Sample an index from a weighted discrete distribution.

    Parameters
    ----------

    cdv: np.ndarray, shape = (nr, )
        Cumulative distribution vector associated with the propensity
        vector.

    Returns
    -------

    index: int
        The index in [0, nr - 1] sampled according to the propensity weights.
    """
    # sample
    p = np.random.uniform()
    # find right index of where p would be inserted
    index = cdv.searchsorted(p, side='right')

    return index
