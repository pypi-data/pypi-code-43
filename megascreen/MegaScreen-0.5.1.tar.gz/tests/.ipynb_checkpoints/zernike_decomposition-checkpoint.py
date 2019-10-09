# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.1.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import numpy as np
import matplotlib.pyplot as plt
from joblib import Memory, Parallel, delayed
import MegaScreen
from zernike import ZernikeGrid, jtonm
from astropy.table import Table
import time

# Incantation to get latest version
import test_Noll
import importlib
importlib.reload(test_Noll)
from test_Noll import *

# %% [markdown]
# # Test the simulator against Winker 1991

# %%
# Use the joblib Memory decorator to avoid having to recompute long-running calculations
memory = Memory("cache", verbose=0)
@memory.cache
def MemoWinker(
    diameter=32,
    L0Min=16,
    L0Max=8000,
    numL0=20,
    numIter=100,
    maxRadial=2,
    nfftOuter=256,
    nfftInner=256,
    randomSeed=12345,
):
    """Memoised wrapper for the Winker function"""
    np.random.seed(randomSeed)
    return Winker(
        diameter, L0Min, L0Max, numL0, numIter, maxRadial, nfftOuter, nfftInner
    )


t = MemoWinker(numIter=1000, diameter=100, randomSeed=5432112)


# %%
def PlotWinker(t, diameter):
    """Reproduce Fig 2 from Winker 1991"""
    # Plot theoretical values
    L0=np.logspace(0,3,50)
    resid=winker_residual(L0,2)
    for n in range(len(resid)):
        plt.loglog(1/(L0),resid[n],ls="dotted")
    # Plot simulation values
    L0 = 2 * t["L0"] / diameter
    for z in [0, 2, 5]:
        plt.loglog(1 / L0, t["Z" + str(z)], label="Z_max=" + str(z+1))
    plt.legend()

def winker_residual(L0,max_n):
    resid=np.empty((max_n+1,len(L0)))
    for i in range(len(L0)):
        L=L0[i]
        resid[0,i]=winker_piston_residual(L0=L)
        for n in range(1,max_n+1):
            resid[n,i]=resid[n-1,i]-winker_variance_quad(n,R=1,r0=2,L0=L)*(n+1)
    return resid

plt.figure(figsize=(12,10))
plt.xlabel(r"$R/L_0$")
plt.ylabel("$Z_j$")
plt.title("Simulation of Winker Fig 2")
PlotWinker(t, 100)

# %%
