#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 16:55:42 2019

@author: Gabriele Coiana
"""

import numpy as np


import cell, bz, plot, read

def corr(tall,X,tau,mode):
    M = len(tall)
    dt = tall[1] - tall[0]
    tmax = M - tau
    N = np.size(X[0])   
    X0 = X[0:tmax,:]
    X2 = 1/tmax*np.sum(X[0:tmax,:]*X[0:tmax,:])
    C = []
    for n in range(tau):
        Xjj = X[n:n+tmax,:]
        a = np.multiply(np.conjugate(X0),Xjj)
        b = 1/(tmax) * np.sum(a,axis=0)#/X2
        c = np.multiply(b,1)
        if (mode=='projected'):
            d = 1/N*(c)
        else:
            d = 1/N*np.sum(c)
        C.append(d)
    C = np.array(C)
    t = np.arange(0,tau)*dt
    freq = np.fft.fftfreq(tau,d=dt)
    Z = np.fft.fft(C,axis=0)
    return t, C, freq, Z


# =============================================================================
# 
ensemble = 'NPE'
system = 'relax'


file_eigenvectors = 'qpoints_'+system+'_4.0.yaml'
datafile = 'data_pos_'+ensemble
N1,N2,N3 = 8,8,8
N1N2N3 = N1*N2*N3
N = N1N2N3*5
a = 8
masses = np.repeat([137.327, 47.867, 15.9994,15.9994,15.9994],3)#*1822.9 #if you want atomic units, 1 a.u. = 1822.9 amu
# =============================================================================

Nqpoints, qpoints_scaled, ks, freqs, eigvecs = read.read_phonopy(file_eigenvectors)

R0 = cell.BaTiO3(a).get_supercell(a,N1,N2,N3)  #cubic R0
R0 = np.loadtxt('../R0')                       #rhombo R0
R0 = np.repeat(R0,3,axis=0)


Rt = np.loadtxt('../'+datafile)[400::,1:]
Num_timesteps = int(len(Rt[:,0]))
print('Number of timesteps of simulation: ', Num_timesteps, '\n')
tall = np.arange(Num_timesteps)*30*30*2.418884254*1e-05 #conversion to picoseconds
dt = tall[1]-tall[0]
tau = 500
meta = int(tau/2)
Vt = np.gradient(Rt,dt,axis=0)  


### =============================================================================
### Decomposition
Zs = np.zeros((meta,Nqpoints))
print('Now performing decomposition... ')
for i in range(Nqpoints):
    eigvec = eigvecs[i]
    k = ks[i]
    freq_disp = freqs[i]
    print('\tkpoint:  ',k)
    
    Vcoll = np.zeros((Num_timesteps,15),dtype=complex)  
    for j,h,l in zip(range(15),np.repeat(range(0,N),3)*N1N2N3*3,np.tile(range(0,3),5)):
        vels = Vt[:,h+l:h+N1N2N3*3:3]
        poss = R0[h:h+N1N2N3*3:3,:]
        x = np.multiply(vels,np.exp(1j*np.dot(poss,k)))
        Vcoll[:,j] = 1/np.sqrt(N1N2N3)*np.sum(x,axis=1)
    Tkt = Vcoll*np.sqrt(masses)
    
    
    t, C, freq, Gtot = corr(tall,Tkt,tau, ' ')
    Ztot = np.sqrt(np.conjugate(Gtot)*Gtot)
    
    Zs[:,i] = Ztot[0:meta]
### =============================================================================

np.savetxt('Zs_'+ensemble,Zs)
np.savetxt('freq',freq[0:meta])
k_symb = ['$\Gamma$','','','','X','','','','M','','','','$\Gamma$','','','','Z']
plot.plot_k(freq[1:meta],Zs[1::,:],k_symb,freqs,title=file_eigenvectors)
