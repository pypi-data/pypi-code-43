import numpy as np

description = """
This file contains the analytical solution to the 1D Poisson problem.

The solutions it returns are u(x).

This is a good one to converge to numerically.
"""

default_parameters = {
    'k':1.0,
    'f': lambda x : 1.0,
}

class PoissonEquation1D():
    name = 'PoissonEquation1D'
    space_dim = 1
    time_dep = False
    ptdim = 1
    outputs = ['u']

    def __init__(self,params=default_parameters):
        self.params = params.copy()
        # Yoink out the parameters
        K_d = params['K_d']
        K_s = params['K_s']
        K_f = params['K_f']
        phi = params['phi']
        k_eta = params['k']/params['eta']
        domH = 1.0
        self.source = params['source']
        # Only onle coefficent
        alpha = biot = 1.0 - K_d / K_s
        M = K_s/(alpha-phi*(1.0-K_s/K_f))
        self.k = k_eta / self.source
    def __call__(self, xt):
        k = self.k
        panal = np.empty(X.shape[0])
        t = lambda k,x,y : np.sin(k*np.pi*(1.0+x)/2.0)/( k*k*k * np.sinh( k*np.pi )) * \
            ( np.sinh( k*np.pi*(1.0+y)/2.0 ) + np.sinh( k*np.pi*(1.0-y)/2.0) )
        for i,y in enumerate(X):
            panal[i] = (1.0-xt[0]**2.0)/2.0 - 16.0/(np.pi)**3 * \
                sum([t(k,yt[0],yt[1]) for k in xrange(1,101,2) ])
        return {'P':panal}


tests = [SquarePoisson]
