#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 21:59:16 2019

@author: jkl
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import time
plt.ioff()
from tools.invertEMFullFunc import fMaxwellQ, fMaxwellECa, fCS
plt.close('all')


def addnoise(x, level=0.02):
    return x + np.random.randn(1) * x * level
addnoise = np.vectorize(addnoise)


def buildSecondDiff(ndiag):
    x=np.ones(ndiag)
    a=np.diag(x[:-1]*-1,k=-1)+np.diag(x*2,k=0)+np.diag(x[:-1]*-1,k=1)
    a[0,0]=1
    a[-1,-1]=1
    return a


#%%
conds = np.array([20, 30, 20, 50])
depths = np.array([0.5, 1, 1.5])
ec0 = 25 # mS/m
conds0 = np.ones(len(conds))*ec0

fmodel = fCS # 0.011 s
#fmodel = fMaxwellECa # 0.099 s
#fmodel = fMaxwellQ # 0.195 s

cpos = ['vcp','vcp','vcp','hcp','hcp','hcp']
cspacing = [0.32, 0.71, 1.18, 0.32, 0.71, 1.18]

# create ECa
app = fCS(conds, depths, cspacing, cpos)
#app = addnoise(app)

L = buildSecondDiff(len(conds))
def objfunc(p, app):
    return np.sqrt((np.sum((app - fmodel(p, depths, cspacing, cpos))**2)
                          + 0.07*np.sum(np.dot(L, p[:,None])**2))/len(app))
t0 = time.time()
res = minimize(objfunc, conds0, args=(app,), method='Nelder-Mead')
print(res)
print('{:.3f}s'.format(time.time() - t0))

    
#%%   see if we can speed-up minimize by decreasing iteration number
nits = [0, 1, 2, 3, 10, 20, 50, 100, 1000]
rmseECs = []
rmseECas = []
elapseds = []
for nit in nits:
    t0 = time.time()
    res = minimize(objfunc, conds0, args=(app,), method='L-BFGS-B',
                   options={'maxiter':nit})
    elapsed = time.time() - t0
    print(res.x)
    rmseEC = np.sqrt(np.sum((res.x - conds)**2)/len(conds))
    rmseECa = np.sqrt(np.sum((fmodel(res.x, depths, cspacing, cpos) - app)**2)/len(app))
    rmseECs.append(rmseEC)
    rmseECas.append(rmseECa)
    elapseds.append(elapsed)
    print('nit={:d} in {:.3f}s with RMSE={:.2f}'.format(nit, elapsed, rmseECa))
    

fig, ax = plt.subplots()
ax.semilogx(nits, rmseECs, '.-', label='RMSE (EC)')
ax.semilogx(nits, rmseECas, '.-', label='RMSE (ECa)')
ax.legend()
ax2 = ax.twinx()
ax2.semilogx(nits, elapseds, 'k.--', label='time (sec)')
ax.set_xlabel('Max Number of Iteration')
ax.set_ylabel('RMSE')
ax2.set_ylabel('Elasped [s]')
fig.tight_layout()
fig.show()

''' 10 iterations is a good trade-off
'''

    #%%
    solvers = ['Nelder-Mead', 'Powell', 'CG', 'BFGS',
               'L-BFGS-B', 'TNC', 'COBYLA', 'SLSQP']
    tt = []
    for solver in solvers:
        print(solver)
        t0 = time.time()
        res = minimize(objfunc, k.conds0, args=(app,), method=solver)
        tt.append([time.time() - t0, res.nfev, res.fun])
    
    tt = np.vstack(tt)
    xx = np.arange(len(solvers))
    fig, ax = plt.subplots()
    ax.plot(xx, tt)
    ax.set_xticks(xx)
    ax.set_xticklabels(solvers, rotation=90)
    fig.tight_layout()
    fig.show()
    