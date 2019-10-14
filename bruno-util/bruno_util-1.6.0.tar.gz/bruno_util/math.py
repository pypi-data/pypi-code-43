import numpy as np


def center_by_mass(x, particle_axis=0):
    """Subtract center of mass (unweighted) from a collection of vectors
    corresponding to particles's coordinates."""
    shape = x.shape
    # center of mass is the average position of the particles, so average over
    # the particles
    centers_of_mass = np.mean(x, particle_axis)
    # tile the centers of mass for clean elementwise division
    # is there a way to do this faster by relying on numpy's array projection
    # semantics?
    tile_shape = [shape[i] if i == particle_axis else 1
                  for i in range(len(shape))]
    centers_of_mass = np.tile(centers_of_mass, tile_shape)
    return x - centers_of_mass

def locally_linear_fit(x, y, window_size=5, **kwargs):
    """Plots the local slope of y(x) using a moving average with the given
    window size. Passes kwargs onto ax.plot."""
    if window_size % 2 == 0:
        raise ValueError('window_size must be odd')
    if window_size < 3:
        raise ValueError('window_size must be at least 3, so that we have at'
                         ' least two points to fit at endpoints of array.')
    lenx = len(x)
    if lenx < 2:
        raise ValueError('Can\'t fit less than 2 points!')
    inc = int(window_size / 2)
    slope = np.zeros_like(x)
    for i in range(lenx):
        imin = np.max([0, i - inc])
        imax = np.min([lenx, i + inc + 1])
        xfit = x[imin:imax]
        yfit = y[imin:imax]
        to_fit = np.isfinite(xfit) & np.isfinite(yfit)
        if not np.any(to_fit):
            slope[i] = np.nan
        else:
            slope[i], intcpt, r_val, p_val, std_err = stats.linregress(xfit[to_fit], yfit[to_fit])
    ax = kwargs.pop('axes', None)
    if ax is not None:
        ax.plot(x, slope, **kwargs)
    return ax, slope

def deriv(y, x=None, method='fourier'):
    """Calculate the numerical derivative of data

    Different than calculating a numerical derivative given a function (for
    which scipy provides appropriate routines, this function assumes you are
    given some data points :math:`(x, y)_i` that represent a function :math:`y
    = f(x) + \xi` for some noise term :math:`xi`.

    We will eventually provide multiple FFT-based derivatives, along with some
    finite differences methods designed to be more resistant to noisy data.


    Notes
    -----
    `method='fourier'` will correspond to first re-sampling the data onto a
    grid via interpolation if necessary, then performing a FFT, multiplying by
    :math:`2\pi{}ik`, then reversing the FFT.

    Greengard and Lee
    (https://math.nyu.edu/faculty/greengar/glee_nufft_sirev.pdf) provide
    another way to evaluate the FFT on a non-uniform grid, but we use our
    simpler method for now.
    """
    raise NotImplementedError("TODO")


def Kf(r,alf,bet,z):
    res = (1/(np.pi*alf))*r**((1-bet)/alf)*np.exp(-r**(1/alf))
    res *= r*np.sin(np.pi*(1-bet))- z*np.sin(np.pi*(1-bet+alf))
    res /= r**2 - 2*r*z*np.cos(np.pi*alf) + z**2
    return res

def P(phi,alf,bet,eps,z):
    w = eps**(1/alf)*np.sin(phi/alf) + phi*(1+(1-bet)/alf)
    res = eps**(1+(1-bet)/alf)/(2*np.pi*alf)
    res *= np.exp(eps**(1/alf))*(np.cos(w)+1j*np.sin(w))
    res /= eps*np.exp(1j*phi)
    return res

def mlf2(z,alf,bet,K=10):
    """Mittag-Leffler"""
    e = 1/gamma(bet)
    for k in range(1,K):
        e += z**k/gamma(alf*k+bet)
    return e

#TODO finish and test
# @jit(nopython=True)
# def mittag_leffler(z, alpha, beta, K=10):
#     r"""
#     Computes the generalized Mittag-Leffler function, :math:`E_{\alpha,\beta}(z)`

#     This function follows the paper by Gorenflo, Loutchko and Luchko."""
#     rho = 1e-10
#     # scale alpha to alpha < 1
#     if alpha > 1:
#         k0 = int(np.floor(alpha)+1)
#         e = 0
#         for k in range(0, k0-1 + 1):
#             z1 = z**(1/k0)
#             w = np.exp(1j* 2 * np.pi*k/k0)
#             e += (1/k0)*mlf( z1*w, alf/k0, bet,K)
#         return e
#     elif abs(z) < 1e-6:
#         return 1/gamma(bet)
#     elif abs(z) < 1:
#         k0 = max(np.ceil((1-bet)/alf),
#                  np.ceil(np.log(rho*(1-np.abs(z)))/np.log(np.abs(z))))
#         e = 0
#         for k in range(1, k0):

#     elif abs(z) > np.floor(10+5*alf):
#         k0 = int(np.floor(-np.log(rho)/np.log(abs(z))))
#     elif abs(np.angle(z)) < alf*np.pi/4 + 0.5*min(np.pi,alf*np.pi):
#         e = (1/alf)*z**((1-bet)/alf)*np.exp(z**(1/alf))
#         for k in range(1,k0):
#             e += z**(-k)/gamma(bet-alf*k)
#         return(e)
#     else:
#     e = 0
#     for k in range(1,k0):
#     t = z**(-k)/gamma(bet-alf*k)
#     e += -t
#     print(‘ML=’,e)
#     return(e)
#     else:
#     eps = 0.1
#     I1,err = quad(Kf,eps,np.inf,args=(alf,bet,z))
#     I2,err2 = quad(P,-np.pi*alf,np.pi*alf,args=(alf,bet,eps,z))
#     print(‘integral case: ML=’,I1+I2)
#     print(‘z=’,z)
#     print(‘alpha=’,alf)
#     print(‘beta=’,bet)
#     return I1+I2
#     return 0

# def mlfn( z, a, b, n):
# if n==0:
# return mlf(z,a,b)
# else:
# h = mlfn(z,a,b-1,n-1)
# A = mlfn(z,a,b,n-1)
# h += (b-float(n-1)*a-1)*float(A)
# return (1/z)*h

# def fpp2( delta, nu,n,t):
# z = nu*t**delta
# return z**n*mlfn(-z,delta,1,n)
