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
from joblib import Memory
import test_Noll
import importlib
importlib.reload(test_Noll)
from test_Noll import Winker, Noll

memory = Memory("cache", verbose=0)


# %%
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
        diameter,
        L0Min,
        L0Max,
        numL0,
        numIter,
        maxRadial,
        nfftOuter,
        nfftInner)
t=MemoWinker(numIter=10000)


# %%
def PlotWinker(t,diameter,fmin=1e-3,fmax=1e0):
    L0=2*t["L0"]/diameter
    for z in [0,2,5]:
        plt.loglog(1/L0,t["Z"+str(z)],label="Z"+str(z))
        plt.loglog([fmin,fmax],[Noll[z],Noll[z]],ls="dotted")
PlotWinker(t,32)

# %%
