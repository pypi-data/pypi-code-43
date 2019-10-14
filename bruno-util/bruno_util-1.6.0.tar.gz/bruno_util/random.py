import os
import struct
import numpy as np
# from .utils import well_behaved_decorator
from functools import wraps

def strong_default_seed(f):
    """Use os.random to correctly seed a np.random.RandomState-compatible
    random variate if the user does not provide the "seed" random variable. The
    correctly initialized state is passed to the function via the "random_state"
    kwarg.

    Parameters
    ----------
    f : Callable
        function that takes at least two kwargs, seed and random_state. random_state should
        be used to generate random numbers within the function.

    Returns
    -------
    wrapped_f : Callable
        Function that initializes random_state (using seed, or by generating a seed if
        none is given) if it is not passed to the function.

    Notes
    -----
    On sane operating systems, you should be able to parallelize the function
    and get different results for each invocation by letting this wrapper
    initiazlie the seed at each call site.
    """
    @wraps(f)
    def wrapped_f(*args, **kwargs):
        if 'random_state' in kwargs and kwargs['random_state'] is not None:
            return f(*args, **kwargs)
        if 'seed' not in kwargs or kwargs['seed'] is None:
            seed = struct.unpack("<L", os.urandom(4))[0]
        else:
            seed = kwargs['seed']
        random_state = np.random.RandomState()
        random_state.seed(seed)
        kwargs['random_state'] = seed
        return f(*args, **kwargs)
    return wrapped_f

def make_pool(rvs_f, pool_size=1024, unit_size=tuple(), **kwargs):
    """Use a random variate generator that takes a "size" keyword to make a
    function that just return random values "one" at a time from a pre-computed
    pool, replenishing the pool as necessary.

    This often provides serious speedups over calling the function with
    size=unit_size repeatedly when usign numpy/scipy random generation
    functions.

    .. warning::

        `kwargs` are passed on to the `rvs_f` function when it is called to
        replenish the pool. This means if `kwargs` is constantly changing, many
        of its values will be ignored.

    Parameters
    ----------

    rvs_f : Callable
        function that takes size kwarg and generates that many random numbers
    pool_size : int
        how many sets of random numbers to generate ahead of time. this is how
        many times the function we generate can be called before replenishing
        its pool.
    unit_size : Tuple[int]
        the shape of the set of random numbers to be returned every time the
        wrapped function is called

    Returns
    -------

    wrapped_rvs_f : Callable
        function that returns random array of shape unit_size every time it is
        called (ignores all arguments) from a precomputed pool.
    """
    def rv():
        if rv.ri == pool_size:
            rv.rand_pool = rvs_f(size=((pool_size, )+unit_size), **kwargs)
            rv.ri = 0
        rv.ri += 1
        return rv.rand_pool[rv.ri - 1]
    rv.rand_pool = rvs_f(size=((pool_size,)+unit_size), **kwargs)
    rv.ri = 0
    return rv

