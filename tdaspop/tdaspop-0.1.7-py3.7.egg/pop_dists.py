"""
Distributions often needed for sampling populations 
"""
__all__ = ['double_gaussian']

import numpy as np


def double_gaussian(mode, sigmam, sigmap, size=1000,
                    rng=np.random.RandomState(1)):
    """Draw samples from a double gaussian distribution


    Parameters
    ----------
    mode: `np.float`
	mode of the distribution.
    sigmam: `np.float`
	standard deviation of the distribution
    sigmap: `np.float`
	standard deviation of the distribution
    size: int
	number of samples required
    rng: instance `np.random.RandomState`, defaults to state with seed 1.

    Returns
    -------
    samples: `np.ndarray`
    samples from the double gaussian distribution with given parameters.

    Notes
    -----
    This code is essentially the same as code contributed by D. Rubin for SN.
    """
    # Stick to a convention sigmam is a +ve number
    sigs = np.abs([sigmam, sigmap])
    probs = sigs/sigs.sum()
    sigsamps = rng.choice((-sigs[0], sigs[1]), size=size, replace=True, p=probs)
    samps = np.abs(rng.normal(0., 1., size=size))
    return samps * sigsamps + mode
