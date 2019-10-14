import numpy as np
from numba import jit

from functools import reduce

@jit(nopython=True)
def where(element, test_elements, assume_sorted=True):
    """Return indices of `test_element` containing each element of
    `element` (np.nan otherwise), for case where `test_elements` is an array of unique
    values. Broadcasts over `element`, so returned array has that same size.

    Parameters
    ----------
    element : (N,) array_like
        elements to search for in `test_elements`
    test_elements : (M,) array_like
        array to extract locations out of
    assume_sorted : bool
        whether or not test_elements is sorted. will internally sort if False

    Returns
    """
    if assume_sorted:
        ixs = np.arange(len(test_elements))
    else:
        ixs = np.argsort(test_elements)
        test_elements = test_elements[ixs]
    elem_ix = np.argsort(element)
    elem = element[elem_ix]
    wi = np.zeros_like(element)
    ti = 0
    for ei, e in enumerate(elem):
        #TODO: if log(len(unique(elem))) <<< elem, use binary search instead of
        # linear search here for big speedup
        while test_elements[ti] < e:
            ti += 1
        if test_elements[ti] > e:
            wi[ei] = np.nan
        else:
            wi[ei] = ixs[ti] # works whether or not assume_sorted
    return wi

def loglinspace(Ntot, Nlog, Nlin):
    """Union of linspaces with log-spaced ends, same start.

    Whenever you want to use simulation output to calculate some type of
    correlation (e.g. MSD from BD), you typically want to linearly space points
    so that you can use sliding windows to easily compute the time-averaged
    correlation function.

    But then, in order to get statistics for the whole range of time scales
    covered by the simulation, it would naively seem that one needs to save
    *every* time point, which is extremely wasteful.

    Instead, one can save linear spaced points with different frequencies, to
    cover the different orders of magnitude. For example, you might simulate
    using the grid:

        >>> import numpy as np
        >>> t = np.arange(0, 1e8, 1e-2)

    but only save at times:

        >>> from functools import reduce
        >>> save_time_arrs = [np.arange(0, 1e2, 1e-2),
                np.arange(0, 1e4, 1e0), np.arange(0, 1e6, 1e2),
                np.arange(0, 1e8, 1e4)]
        >>> t_save = reduce(np.union1d, save_time_arrs)

    if we have the simulation output at any of the individual members of
    `save_time_arrs`, we can use a simple sliding window to calculate
    time-averaged correlation functions of our system over (in this case)
    `1e4` time points.

    But if we pass just `t_save` to a simulation function, the output will have
    each of these different evenly-space arrays interleaved with each other.
    The purpose of this function is to return an appropriate `t_save` given `t`
    and a specification of how much overlap there should be between
    adjacent `linspace`'s, as well as an array of indices for extracting each
    `save_time_arrs` member from `t_save` (and thus, how to extract
    evenly-spaced simulation time points from the interleaved, quasi-log-spaced
    simulation time points requested by `t_save`.

    Parameters
    ----------
    Ntot : int
        length of `t`
    Nlog : int
        number of log-spaced intervals
    Nlin : int
        number of linearly-space points per interval

    Returns
    -------
    t_save : (<= Nlog*Nlin,) array_like
        subset of t
    save_i : List<np.array>
        a Nlog-length list of Nlin-long 1d arrays of indices. for each `i`,
        t_save[save_i[i]] will extract one of the linearly-space sets of points

    Usage
    -----
    In order to  generate the example from earlier in this docstring, simply
    use:

        >>> t = np.linspace(0, 1e8, 1e10+1)
        >>> t_save, save_i = loglinspace(t, 4, 1e4)

    Then you can do, for example, some BD simulations:

        >>> import wlcsim.bd as bd
        >>> x = bd.rouse.jit_rouse(N=101, L=100, b=1, D=1, t=t, t_save=t_save)

    and compute the taMSD from this trajectory over all 10 orders of magnitude
    in time using "blocks" of `1e4` points at a time like:

        >>> msds = np.zeros_like(t_save)
        >>> for si in save_i:
        >>>     ts = t_save[si]
        >>>     c, m = bd.runge_kutta._get_bead_msd(x[si], 51) # mid-point bead
        >>>     # recombine into single array, overwriting values computed from
        >>>     # more tightly-space points with those from less tightly-spaced
        >>>     msds[si] = m/c
        >>>     # or just plot directly
        >>>     plt.plot(ts[1:], m[1:]/c[1:], 'k.')

    """
    raise NotImplementedError("Doesn't do as advertised....docstring is out of sync.")
    end = np.log10(Ntot)
    log_step = end/Nlog
    # e.g. np.log10(1e8)/4 -> step=2, ends=(2, 4, 6, 8)
    log_ends = np.arange(log_step, end+1, log_step)
    save_time_arrs = [np.linspace(0, np.power(10, e), Nlin) for e in log_ends]
    t_save = reduce(np.union1d, save_time_arrs)
    save_i = [where(t, t_save) for t in save_time_arrs]
    return t_save, save_i

def loglinrange(start, stop, dt, Nlin, overlap=0):
    """As linlogspace but an easier API.

    Chooses a subset of `np.arange(start, stop, dt)` that is made of linearly
    spaced points of differing distances apart, so that you only need
    `Nlin*np.log((stop-start)/dt)` points to cover the interval.

    Parameters
    ----------
    start : float
        The start of the first linspace'd region
    stop : float
        The end of the last linspace'd region
    dt : float
        The step size for the smallest region, i.e. `np.arange(start, start+(Nlin+1)*dt, dt)`
    Nlin : float
        the size of the linspace'd regions (in # points)
    overlap : float, :math:`\in[0,1)`
        how much the next region should overlap with the previous in log space
    """
    if overlap < 0 or overlap >= 1:
        raise ValueError("`overlap` must be in [0,1)")
    # index of each t_arr at which next t_arr should start to create the
    # correct `overlap` (log spaced interpolation)
    # at 1-overlap=0, we want the multiplier to be 1 and the index to be 0
    # (start over at same place)
    # at 1-overlap=1, we want the multiplier to be `Nlin`, and the index will
    # not exist (Nlin+1)
    #TODO: BUG: this works at overlap=0 just fine, but otherwise there seems to
    # be an offset between loglinrange and loglinsample, which grows larger as
    # overlap increases
    log_i = np.interp(x=(1 - overlap), xp=[0, 1], fp=[np.log10(1), np.log10(Nlin)])
    overlap_i = np.round(np.power(10.0, log_i)).astype(int)

    t = start
    t_arrs = []
    while t < stop:
        t_end = t + (Nlin+1)*dt
        t_arr = np.arange(t, t_end, dt)
        t_arrs.append(t_arr[t_arr < stop])
        # still on np.arange(start, stop, dt) grid by selecting directly from it
        t = t_arr[overlap_i]
        # since overlap_i is rounded, should stay on original grid as well
        dt *= overlap_i
    t_save = reduce(np.union1d, t_arrs)
    save_i = [where(t, t_save) for t in t_arrs]
    return t_save, save_i

def test_loglinrange():
    """Should remain a subset of np.arange when applicable"""
    t, i = bnp.loglinrange(0, 1e4, 1, 1e2, 0.5)
    t_all = np.arange(0, 1e4, 1)
    assert(np.all(np.isin(t, t_all)))
    # # this fails because of floating round-off
    # t, i = bnp.loglinrange(0, 1e4, 0.17, 1e2, 0.5)
    # t_all = np.arange(0, 1e4, 0.17)
    # assert(np.all(np.isin(t, t_all)))

def loglinsample(Ntot, Nlin, overlap):
    """Preferred version of loglin* functions.

    Sometimes, because of rounding errors,

        >>> np.isin(bnp.loglinrange(start, stop, dt, ...),
                    np.arange(start, stop, dt))

    will have some `False` values, because the two arrays are off by floating
    point mismatch sized differences.

    This function instead of returning absolute times, returns indices into the
    original `np.arange(start, stop, dt)` array, so that we can ensure no such
    error occurs."""
    t, i = loglinrange(0, Ntot+1, 1, Nlin, overlap)
    return np.round(t).astype(int), i

def test_loglinsample():
    """compare to loglinrange.

    WARNING: BUG: apparently only works currently for small enough `overlap`"""
    istart = 0
    stop = 1e4
    dt = 0.17
    Nlin = 1e2
    overlap = 0.2 # for overlap >= 0.3ish, this test fails

    # actual baseline grid
    t_all = np.arange(start, stop, dt)
    Ntot = len(t_all)
    # get spacing via sub-sampling
    ti, ii = bnp.loglinsample(Ntot, Nlin, overlap)
    ts = t_all[ti]
    # get spacing via direct sampling
    t, i = bnp.loglinrange(start, stop, dt, Nlin, overlap)
    # compare results
    assert(np.all(np.isclose(t, ts)))
