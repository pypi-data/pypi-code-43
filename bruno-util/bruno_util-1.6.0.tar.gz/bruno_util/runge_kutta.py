import numpy as np
from numba import jit

# for testing
import pandas as pd
import scipy.stats
import matplotlib.pyplot as plt


def rkf( f, a, b, x0, tol, hmax, hmin ):
    """Runge-Kutta-Fehlberg method to solve x' = f(x,t) with x(t[0]) = x0.

    USAGE:
        t, x = rkf(f, a, b, x0, tol, hmax, hmin)

    INPUT:
        f     - function equal to dx/dt = f(x,t)
        a     - left-hand endpoint of interval (initial condition is here)
        b     - right-hand endpoint of interval
        x0    - initial x value: x0 = x(a)
        tol   - maximum value of local truncation error estimate
        hmax  - maximum step size
        hmin  - minimum step size

    OUTPUT:
        t     - NumPy array of independent variable values
        x     - NumPy array of corresponding solution function values

    NOTES:
        This function implements 4th-5th order Runge-Kutta-Fehlberg Method
        to solve the initial value problem

           dx
           -- = f(x,t),     x(a) = x0
           dt

        on the interval [a,b].

        Based on pseudocode presented in "Numerical Analysis", 6th Edition,
        by Burden and Faires, Brooks-Cole, 1997.
    """

    # Coefficients used to compute the independent variable argument of f

    a2  =   2.500000000000000e-01  #  1/4
    a3  =   3.750000000000000e-01  #  3/8
    a4  =   9.230769230769231e-01  #  12/13
    a5  =   1.000000000000000e+00  #  1
    a6  =   5.000000000000000e-01  #  1/2

    # Coefficients used to compute the dependent variable argument of f

    b21 =   2.500000000000000e-01  #  1/4
    b31 =   9.375000000000000e-02  #  3/32
    b32 =   2.812500000000000e-01  #  9/32
    b41 =   8.793809740555303e-01  #  1932/2197
    b42 =  -3.277196176604461e+00  # -7200/2197
    b43 =   3.320892125625853e+00  #  7296/2197
    b51 =   2.032407407407407e+00  #  439/216
    b52 =  -8.000000000000000e+00  # -8
    b53 =   7.173489278752436e+00  #  3680/513
    b54 =  -2.058966861598441e-01  # -845/4104
    b61 =  -2.962962962962963e-01  # -8/27
    b62 =   2.000000000000000e+00  #  2
    b63 =  -1.381676413255361e+00  # -3544/2565
    b64 =   4.529727095516569e-01  #  1859/4104
    b65 =  -2.750000000000000e-01  # -11/40

    # Coefficients used to compute local truncation error estimate.  These
    # come from subtracting a 4th order RK estimate from a 5th order RK
    # estimate.

    r1  =   2.777777777777778e-03  #  1/360
    r3  =  -2.994152046783626e-02  # -128/4275
    r4  =  -2.919989367357789e-02  # -2197/75240
    r5  =   2.000000000000000e-02  #  1/50
    r6  =   3.636363636363636e-02  #  2/55

    # Coefficients used to compute 4th order RK estimate

    c1  =   1.157407407407407e-01  #  25/216
    c3  =   5.489278752436647e-01  #  1408/2565
    c4  =   5.353313840155945e-01  #  2197/4104
    c5  =  -2.000000000000000e-01  # -1/5

    # Set t and x according to initial condition and assume that h starts
    # with a value that is as large as possible.

    t = a
    x = x0
    h = hmax

    # Initialize arrays that will be returned

    T = np.array( [t] )
    X = np.array( [x] )

    while t < b:

        # Adjust step size when we get to last interval

        if t + h > b:
            h = b - t;

        # Compute values needed to compute truncation error estimate and
        # the 4th order RK estimate.

        k1 = h * f( x, t )
        k2 = h * f( x + b21 * k1, t + a2 * h )
        k3 = h * f( x + b31 * k1 + b32 * k2, t + a3 * h )
        k4 = h * f( x + b41 * k1 + b42 * k2 + b43 * k3, t + a4 * h )
        k5 = h * f( x + b51 * k1 + b52 * k2 + b53 * k3 + b54 * k4, t + a5 * h )
        k6 = h * f( x + b61 * k1 + b62 * k2 + b63 * k3 + b64 * k4 + b65 * k5, \
                    t + a6 * h )

        # Compute the estimate of the local truncation error.  If it's small
        # enough then we accept this step and save the 4th order estimate.

        r = abs( r1 * k1 + r3 * k3 + r4 * k4 + r5 * k5 + r6 * k6 ) / h
        if len( np.shape( r ) ) > 0:
            r = np.max( r )
        if r <= tol:
            t = t + h
            x = x + c1 * k1 + c3 * k3 + c4 * k4 + c5 * k5
            T = np.append( T, t )
            X = np.append( X, [x], 0 )

        # Now compute next step size, and make sure that it is not too big or
        # too small.
        # Wikipedia (on page for "adaptive stepsize", uses richardson
        # extrapolation also, but chooses
        # h*min(max(0.9*(tol/r, 0.3), 2)
        h = h * min( max( 0.84 * ( tol / r )**0.25, 0.1 ), 4.0 )

        if h > hmax:
            h = hmax
        elif h < hmin:
            print( "Error: stepsize should be smaller than %e." % hmin )
            break

    # endwhile

    return ( T, X )


def rkfm(f, D, a, b, x0, tol, hmax, hmin):
    """Runge-Kutta-Fehlberg-Maruyama method to solve x' = f(x,t) + R with
    x(t[0]) = x0, where R is an uncorrelated Gaussian process with constant
    diffusivity D.

    USAGE:
        t, x = rkf(f, D, a, b, x0, tol, hmax, hmin)

    INPUT:
        f     - function equal to dx/dt = f(x,t)
        a     - left-hand endpoint of interval (initial condition is here)
        b     - right-hand endpoint of interval
        x0    - initial x value: x0 = x(a)
        tol   - maximum value of local truncation error estimate
        hmax  - maximum step size
        hmin  - minimum step size

    OUTPUT:
        t     - NumPy array of independent variable values
        x     - NumPy array of corresponding solution function values

    NOTES:
        This function implements 4th-5th order Runge-Kutta-Fehlberg Method
        to solve the initial value problem

           dx
           -- = f(x,t),     x(a) = x0
           dt

        on the interval [a,b].

        Based on pseudocode presented in "Numerical Analysis", 6th Edition,
        by Burden and Faires, Brooks-Cole, 1997.
    """

    # Coefficients used to compute the independent variable argument of f
    a2  =   2.500000000000000e-01  #  1/4
    a3  =   3.750000000000000e-01  #  3/8
    a4  =   9.230769230769231e-01  #  12/13
    a5  =   1.000000000000000e+00  #  1
    a6  =   5.000000000000000e-01  #  1/2

    # Coefficients used to compute the dependent variable argument of f
    b21 =   2.500000000000000e-01  #  1/4
    b31 =   9.375000000000000e-02  #  3/32
    b32 =   2.812500000000000e-01  #  9/32
    b41 =   8.793809740555303e-01  #  1932/2197
    b42 =  -3.277196176604461e+00  # -7200/2197
    b43 =   3.320892125625853e+00  #  7296/2197
    b51 =   2.032407407407407e+00  #  439/216
    b52 =  -8.000000000000000e+00  # -8
    b53 =   7.173489278752436e+00  #  3680/513
    b54 =  -2.058966861598441e-01  # -845/4104
    b61 =  -2.962962962962963e-01  # -8/27
    b62 =   2.000000000000000e+00  #  2
    b63 =  -1.381676413255361e+00  # -3544/2565
    b64 =   4.529727095516569e-01  #  1859/4104
    b65 =  -2.750000000000000e-01  # -11/40

    # Coefficients used to compute local truncation error estimate.  These
    # come from subtracting a 4th order RK estimate from a 5th order RK
    # estimate.
    r1  =   2.777777777777778e-03  #  1/360
    r3  =  -2.994152046783626e-02  # -128/4275
    r4  =  -2.919989367357789e-02  # -2197/75240
    r5  =   2.000000000000000e-02  #  1/50
    r6  =   3.636363636363636e-02  #  2/55

    # Coefficients used to compute 4th order RK estimate
    c1  =   1.157407407407407e-01  #  25/216
    c3  =   5.489278752436647e-01  #  1408/2565
    c4  =   5.353313840155945e-01  #  2197/4104
    c5  =  -2.000000000000000e-01  # -1/5

    # Set t and x according to initial condition and assume that h starts
    # with a value that is as large as possible.
    t = a
    x = x0
    h = hmax

    # Initialize arrays that will be returned
    T = np.array([t])
    X = np.array([x])

    while t < b:

        # Adjust step size when we get to last interval
        if t + h > b:
            h = b - t;

        # Compute values needed to compute truncation error estimate and
        # the 4th order RK estimate.
        F_thermal = np.sqrt(2*D/h)*np.random.normal(size=x.shape)
        k1 = h*(F_thermal + f(x, t))
        k2 = h*(F_thermal + f(x + b21*k1, t + a2*h))
        k3 = h*(F_thermal + f(x + b31*k1 + b32*k2, t + a3*h))
        k4 = h*(F_thermal + f(x + b41*k1 + b42*k2 + b43*k3, t + a4*h))
        k5 = h*(F_thermal + f(x + b51*k1 + b52*k2 + b53*k3 + b54*k4, t + a5*h))
        k6 = h*(F_thermal + f(x + b61*k1 + b62*k2 + b63*k3 + b64*k4 + b65*k5, t + a6*h))

        # Compute the estimate of the local truncation error.  If it's small
        # enough then we accept this step and save the 4th order estimate.
        r = abs( r1 * k1 + r3 * k3 + r4 * k4 + r5 * k5 + r6 * k6 ) / h
        if len( np.shape( r ) ) > 0:
            r = np.max( r )
        if r <= tol:
            t = t + h
            x = x + c1 * k1 + c3 * k3 + c4 * k4 + c5 * k5
            # x = x + np.sqrt(2*D*h)*np.random.normal(size=x.shape)
            T = np.append( T, t )
            X = np.append( X, [x], 0 )

        # # Now compute next step size, and make sure that it is not too big or
        # # too small.
        # h = h * min( max( 0.84 * ( tol / r )**0.25, 0.1 ), 4.0 )
        # if h > hmax:
        #     h = hmax
        # elif h < hmin:
        #     #TODO something's buggy with stepsize, see: rouse.rouse(101, 15,
        #     # 17475, 0, 0.0001, 16667), needs hmin=1e-25...
        #     print( "Error: minimum requested stepsize of %e exceeded." % hmin )
        #     break

    return T, X

def rk4_thermal_lena(f, D, t, x0):
    """x'(t) = f(x(t), t) + Xi(t), where Xi is thermal, diffusivity D

    x0 is x(t[0]).

    :math:`f: R^n x R -> R^n`
    """
    t = np.array(t)
    x0 = np.array(x0)
    x = np.zeros(t.shape + x0.shape)
    dts = np.diff(t)
    x[0] = x0
    dxdt = np.zeros((4,) + x0.shape) # one for each RK step
    # at each step i, we use data (x,t)[i-1] to create (x,t)[i]
    # in order to make it easy to pull into a new functin later, we'll call
    # t[i-1] "t0", old x (x[i-1]) "x0", and t[i]-t[i-1] "h".
    for i in range(1, len(t)):
        h = dts[i-1]
        t0 = t[i-1]
        x0 = x[i-1]
        x_est = x0
        Fbrown = np.sqrt(2*D/(t[i]-t[i-1]))*np.random.normal(size=x0.shape)
        dxdt[0] = f(x0, t0) + Fbrown # slope at beginning of time step
        x_est = x0 + dxdt[0]*(h/2) # first estimate at midpoint
        dxdt[1] = f(x_est, t0 + (h/2)) + Fbrown # estimated slope at midpoint
        x_est = x0 + dxdt[1]*(h/2) # second estimate at midpoint
        dxdt[2] = f(x_est, t0 + (h/2)) + Fbrown # second estimated slope at midpoint
        x_est = x0 + dxdt[2]*h # first estimate at next time point
        dxdt[3] = f(x_est, t0 + h) + Fbrown # slope at end of time step
        # final estimate is weighted average of slope estimates
        x[i] = x0 + h*(dxdt[0] + 2*dxdt[1] + 2*dxdt[2] + dxdt[3])/6
    return x

def rk4_thermal_bruno(f, D, t, x0):
    """WARNING: does not converge strongly (autocorrelation function seems
    higher than should be for OU process...), as is...x'(t) = f(x(t), t) +
    Xi(t), where Xi is thermal, diffusivity D

    x0 is x(t[0]).

    :math:`f: R^n x R -> R^n`
    """
    t = np.array(t)
    x0 = np.array(x0)
    x = np.zeros(t.shape + x0.shape)
    dts = np.diff(t)
    x[0] = x0
    dxdt = np.zeros((4,) + x0.shape) # one for each RK step
    Fbrown = np.sqrt(2*D / ((t[1] - t[0])/2))
    # at each step i, we use data (x,t)[i-1] to create (x,t)[i]
    # in order to make it easy to pull into a new functin later, we'll call
    # t[i-1] "t0", old x (x[i-1]) "x0", and t[i]-t[i-1] "h".
    for i in range(1, len(t)):
        h = dts[i-1]
        t0 = t[i-1]
        x0 = x[i-1]
        x_est = x0
        dxdt[0] = f(x0, t0) + Fbrown # slope at beginning of time step
        # random force estimate at midpoint
        Fbrown = np.sqrt(2*D / ((t[i]-t[i-1])/2))*np.random.normal(size=x0.shape)
        x_est = x0 + dxdt[0]*(h/2) # first estimate at midpoint
        dxdt[1] = f(x_est, t0 + (h/2)) + Fbrown # estimated slope at midpoint
        x_est = x0 + dxdt[1]*(h/2) # second estimate at midpoint
        dxdt[2] = f(x_est, t0 + (h/2)) + Fbrown # second estimated slope at midpoint
        x_est = x0 + dxdt[2]*h # first estimate at next time point
        # random force estimate at endpoint (and next start point)
        Fbrown = np.sqrt(2*D / ((t[i]-t[i-1])/2))*np.random.normal(size=x0.shape)
        dxdt[3] = f(x_est, t0 + h) + Fbrown # slope at end of time step
        # final estimate is weighted average of slope estimates
        x[i] = x0 + h*(dxdt[0] + 2*dxdt[1] + 2*dxdt[2] + dxdt[3])/6
    return x

def euler_maruyama(f, D, t, x0):
    t = np.array(t)
    x0 = np.array(x0)
    x = np.zeros(t.shape + x0.shape)
    dts = np.diff(t)
    x[0] = x0
    # at each step i, we use data (x,t)[i-1] to create (x,t)[i]
    # in order to make it easy to pull into a new functin later, we'll call
    # t[i-1] "t0", old x (x[i-1]) "x0", and t[i]-t[i-1] "h".
    for i in range(1, len(t)):
        h = dts[i-1]
        t0 = t[i-1]
        x0 = x[i-1]
        Fbrown = np.sqrt(2*D/(t[i]-t[i-1]))*np.random.normal(size=x0.shape)
        x[i] = x0 + h*(Fbrown + f(x0, t0))
    return x

def srk1_roberts(f, D, t, x0):
    r"""From wiki, from A. J. Roberts. Modify the improved Euler scheme to
    integrate stochastic differential equations. [1], Oct 2012.

    If we have an Ito SDE given by

    .. math::

        d\vec{X} = \vec{a}(t, \vec{X}) + \vec{b}(t, \vec{X}) dW

    then

    .. math::

        \vec{K}_1 = h \vec{a}(t_k, \vec{X}_k) + (\Delta W_k - S_k\sqrt{h}) \vec{b}(t_k, \vec{X}_k)
        \vec{K}_2 = h \vec{a}(t_{k+1}, \vec{X}_k + \vec{K}_1) + (\Delta W_k - S_k\sqrt{h}) \vec{b}(t_{k+1}, \vec{X}_k + \vec{K}_1)
        \vec{X}_{k+1} = \vec{X}_k + \frac{1}{2}(\vec{K}_1 + \vec{K}_2)

    where :math:`\Delta W_k = \sqrt{h} Z_k` for a normal random :math:`Z_k \sim
    N(0,1)`, and :math:`S_k=\pm1`, with the sign chosen uniformly at random
    each time."""
    t = np.array(t)
    x0 = np.array(x0)
    x = np.zeros(t.shape + x0.shape)
    dts = np.diff(t)
    # -1 or 1, p=1/2
    S = 2*(np.random.random_sample(size=t.shape) < 0.5) - 1
    x[0] = x0
    # at each step i, we use data (x,t)[i-1] to create (x,t)[i]
    # in order to make it easy to pull into a new functin later, we'll call
    # t[i-1] "t0", old x (x[i-1]) "x0", and t[i]-t[i-1] "h".
    for i in range(1, len(t)):
        h = dts[i-1]
        t0 = t[i-1]
        x0 = x[i-1]
        dW = np.random.normal(size=x0.shape)
# D = sigma^2/2 ==> sigma = np.sqrt(2*D)
        Fbrown = np.sqrt(2*D/h)*(dW - S[i])
        # estimate for slope at interval start
        K1 = f(x0, t0) + Fbrown
        Fbrown = np.sqrt(2*D/h)*(dW + S[i])
        # estimate for slope at interval end
        K2 = f(x0+h*K1, t0+h) + Fbrown
        x[i] = x0 + h * (K1 + K2)/2
    return x

# simple test case
def ou(x0, t, k_over_xi, D, method=rk4_thermal_lena):
    "simulate ornstein uhlenbeck process with theta=k_over_xi and sigma^2/2=D"
    def f(x,t):
        return -k_over_xi*x
    return method(f, D=D, t=t, x0=x0)

@jit(nopython=True)
def _get_scalar_corr(X, t):
    "fast correlation calculation for testing"
    corr = np.zeros_like(t)
    count = np.zeros_like(t)
    for i in range(X.shape[1]):
        for j in range(X.shape[0]):
            for k in range(j, X.shape[0]):
                corr[k-j] += X[k,i]*X[j,i]
                count[k-j] += 1
    return corr, count

@jit
def _get_vector_corr(X, t):
    "fast correlation calculation for testing"
    num_t, num_samples = X.shape
    corr = np.zeros_like(t)
    count = np.zeros_like(t)
    for i in range(num_t):
        for j in range(j, num_t):
            for k in range(num_samples):
                corr[j-i] += X[j,k]@X[i,k]
                count[j-i] += 1
    return corr, count

@jit(nopython=True)
def _get_bead_msd(X, k=None):
    "center bead by default"
    num_t, num_beads, d = X.shape
    if k is None:
        k = max(0, int(num_beads/2 - 1))
    ta_msd = np.zeros((num_t,))
    count = np.zeros((num_t,))
    for i in range(num_t):
        for j in range(i, num_t):
            ta_msd[j-i] += (X[j,k] - X[i,k])@(X[j,k] - X[i,k])
            count[j-i] += 1
    return ta_msd, count

# test different integrators below on simply OU process
def test_ou_autocorr(method=srk1_roberts):
    k = 2
    xi = 4
    kbT = 1
    D = kbT/xi
    k_over_xi = k/xi
    x0 = scipy.stats.norm.rvs(scale=np.sqrt(D/k_over_xi), size=(10_000,))
    t = np.linspace(0, 1e2, 1e3+1)
    X = ou(x0, t, k_over_xi, D, method=method)
    assert(np.abs(np.var(X) - D/k_over_xi)/(D/k_over_xi) < 0.1)
    corr, count = _get_corr(X, t)
    err = corr/count - (kbT/k)*np.exp(-k_over_xi*t)
    plt.figure()
    plt.plot(t, err)
    plt.figure()
    plt.hist(X[-100:].flatten(), bins=100, density=1)
    x = np.linspace(-3, 3, 100)
    plt.plot(x, scipy.stats.norm(scale=np.sqrt(D/k_over_xi)).pdf(x))
    return X

@jit(nopython=True)
def jit_rouse(N, L, b, D, t):
    """ faster version of wlcsim.bd.rouse.rouse using jit """
    zero = np.array([[0,0,0]])
    # derived parameters
    k_over_xi = 3*D/b**2
    L0 = L/(N-1) # length per bead
    Lb = L0/b # kuhn lengths per bead
    # initial position
    x0 = b*np.sqrt(Lb)*np.random.randn(N, 3)
    # x0 = np.cumsum(x0, axis=0)
    for i in range(1,N):
        x0[i] = x0[i-1] + x0[i]
    x = np.zeros(t.shape + x0.shape)
    dts = np.diff(t)
    # -1 or 1, p=1/2
    S = 2*(np.random.rand(len(t)) < 0.5) - 1
    x[0] = x0
    # at each step i, we use data (x,t)[i-1] to create (x,t)[i]
    # in order to make it easy to pull into a new functin later, we'll call
    # t[i-1] "t0", old x (x[i-1]) "x0", and t[i]-t[i-1] "h".
    for i in range(1, len(t)):
        h = dts[i-1]
        t0 = t[i-1]
        x0 = x[i-1]
        dW = np.random.randn(*x0.shape)
# D = sigma^2/2 ==> sigma = np.sqrt(2*D)
        Fbrown = np.sqrt(2*D/h)*(dW - S[i])
        # estimate for slope at interval start
        f = np.zeros(x0.shape)
        for j in range(1,N):
            for n in range(3):
                f[j,n] += -k_over_xi*(x0[j,n] - x0[j-1,n])
                f[j-1,n] += -k_over_xi*(x0[j-1,n] - x0[j,n])
        K1 = f + Fbrown
        Fbrown = np.sqrt(2*D/h)*(dW + S[i])
        # estimate for slope at interval end
        x1 = x0 + h*K1
        f = np.zeros(x0.shape)
        for j in range(1,N):
            for n in range(3):
                f[j,n] += -k_over_xi*(x1[j,n] - x1[j-1,n])
                f[j-1,n] += -k_over_xi*(x1[j-1,n] - x1[j,n])
        K2 = f + Fbrown
        x[i] = x0 + h * (K1 + K2)/2
    return x

@jit(nopython=True)
def jit_rouse_confined(N, L, b, D, t, Aex, rx, ry, rz):
    """ adds an elliptical confinement. energy is like cubed of distance
    outside of ellipsoid, pointing normally back in. times some factor Aex
    controlling its strength """
    zero = np.array([[0,0,0]])
    # derived parameters
    k_over_xi = 3*D/b**2
    L0 = L/(N-1) # length per bead
    Lb = L0/b # kuhn lengths per bead
    # initial position
    x0 = np.random.randn(N, 3)
    x = np.zeros(t.shape + x0.shape)
    dts = np.diff(t)
    # -1 or 1, p=1/2
    S = 2*(np.random.rand(len(t)) < 0.5) - 1
    x[0] = x0
    # at each step i, we use data (x,t)[i-1] to create (x,t)[i]
    # in order to make it easy to pull into a new functin later, we'll call
    # t[i-1] "t0", old x (x[i-1]) "x0", and t[i]-t[i-1] "h".
    for i in range(1, len(t)):
        h = dts[i-1]
        t0 = t[i-1]
        x0 = x[i-1]
        dW = np.random.randn(*x0.shape)
# D = sigma^2/2 ==> sigma = np.sqrt(2*D)
        Fbrown = np.sqrt(2*D/h)*(dW - S[i])
        # estimate for slope at interval start
        f = np.zeros(x0.shape)
        j = 0
        conf = x0[j,0]**2/rx**2 + x0[j,1]**2/ry**2 + x0[j,2]**2/rz**2
        if conf > 1:
            conf_u = np.array([-x0[j,0]/rx**2, -x0[j,1]/ry**2, -x0[j,2]/rz**2])
            conf_u = conf_u/np.linalg.norm(conf_u)
            f[j] += Aex*np.power(conf, 3) # Steph: np.power(np.sqrt(conf) - 1, 3)
        for j in range(1,N):
            conf = x0[j,0]**2/rx**2 + x0[j,1]**2/ry**2 + x0[j,2]**2/rz**2
            if conf > 1:
                conf_u = np.array([-x0[j,0]/rx**2, -x0[j,1]/ry**2, -x0[j,2]/rz**2])
                conf_u = conf_u/np.linalg.norm(conf_u)
                f[j] += Aex*np.power(conf, 3) # Steph: np.power(np.sqrt(conf) - 1, 3)
            for n in range(3):
                f[j,n] += -k_over_xi*(x0[j,n] - x0[j-1,n])
                f[j-1,n] += -k_over_xi*(x0[j-1,n] - x0[j,n])
        K1 = f + Fbrown
        Fbrown = np.sqrt(2*D/h)*(dW + S[i])
        # estimate for slope at interval end
        x1 = x0 + h*K1
        f = np.zeros(x0.shape)
        for j in range(1,N):
            for n in range(3):
                f[j,n] += -k_over_xi*(x1[j,n] - x1[j-1,n])
                f[j-1,n] += -k_over_xi*(x1[j-1,n] - x1[j,n])
        K2 = f + Fbrown
        x[i] = x0 + h * (K1 + K2)/2
    return x

@jit(nopython=True)
def jit_rouse_linked(N, L, b, D, t):
    pass
