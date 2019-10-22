import numpy as np
from webgeodyn.filters import coeffilter, modelfilter, measurefilter
from webgeodyn.data import GHData, TSData


@measurefilter
def keep_m(measure, mmin, mmax):
    """ Filters the measure to keep only the data corresponding to spherical
    harmonics of order mmin <= m <= mmax.
    """
    for k in range(measure.data.shape[1]):
        m = measure.k2lm(k)[1]
        if (m < mmin) or (m > mmax):
            measure.data[:,k] = 0
    return measure


@measurefilter
def keep_sym(measure, isym=True):
    """ Filters the measure to keep only the data corresponding to
    equatorial-symmetric (ES) spherical harmonics for isym=True
    or equatorial-asymmetric (EA) spherical harmonics for isym=False.
    """
    print("isym is ", isym)
    if type(measure) == GHData:
        indices = np.argwhere(((measure.l - measure.m) % 2) == isym)
        measure.data[:,indices] = 0  # Select ES (isym=True) or EA (isym=False) magnetic field coefs
        measure.setData(measure.data)

    elif type(measure) == TSData:
        indices_t_ES = np.argwhere( ((measure.l - measure.m) % 2 != isym) * measure.is_t )
        indices_s_ES = np.argwhere( ((measure.l - measure.m) % 2 == isym) * measure.is_s )
        measure.data[:,indices_t_ES] = 0  # Select ES (isym=True) or EA (isym=False) flow coefs
        measure.data[:,indices_s_ES] = 0  # Select ES (isym=True) or EA (isym=False) flow coefs
        measure.setData(measure.data)

    else:
        # TODO : Perhaps raise a ValueError ? Return None ?
        print('Invalid measure type: only GHData and TSData are accepted')
        return

    return measure
