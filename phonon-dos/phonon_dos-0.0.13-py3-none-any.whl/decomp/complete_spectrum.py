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
# Parameters
a = read.read_parameters()[0]
mba, mti, mo = read.read_parameters()[1:4]
N1,N2,N3 = read.read_parameters()[4:7]
kinput = read.read_parameters()[7::][0]
file_eigenvectors = read.read_parameters()[8]
file_trajectory = read.read_parameters()[9]
file_initial_conf = read.read_parameters()[10]
system = read.read_parameters()[11]
DT = read.read_parameters()[12]
tau = read.read_parameters()[13]
T = read.read_parameters()[14]

N1N2N3 = N1*N2*N3 # Number of cells
N = N1*N2*N3*5    # Number of atoms
masses = np.repeat([mba, mti, mo, mo, mo],N1*N2*N3*3)#*1822.9 #if you want atomic units, 1 a.u. = 1822.9 amu
cH = 1.066*1e-6 # to [H]
cev = 2.902*1e-05 # to [ev]
kbH = 3.1668085639379003*1e-06# a.u. [H/K]
kbev = 8.617333262*1e-05 # [ev/K]
# =============================================================================

print('\nHello, lets start!\n')
print(' Getting input parameters and calculating velocities...')
print(' Temperature: ', T, ' K')
Nqpoints, qpoints_scaled, ks, freqs, eigvecs = read.read_phonopy(file_eigenvectors)

if (system=='norelax'):
    R0 = cell.BaTiO3(a).get_supercell(a,N1,N2,N3)  #cubic R0
if (system=='relax'):
    R0 = np.loadtxt('../R0')                       #rhombo R0
    R0 = np.repeat(R0,3,axis=0)
if (system=='avg'):                                #avg R0
    R0 = np.loadtxt('R0_avg')

Rt = np.loadtxt(file_trajectory)[:,1:]
Num_timesteps = int(len(Rt[:,0]))
print(' Number of timesteps of simulation: ', Num_timesteps, '\n')
tall = np.arange(Num_timesteps)*DT*2.418884254*1e-05 #conversion to picoseconds
dt_ps = tall[1]-tall[0]
#you want the max frequency plotted be 25 Thz
max_freq = 0.5*1/dt_ps
if (max_freq < 25):
    meta = int(tau/2)
else:
    meta = int(tau/2*25/max_freq)
#Vt = np.gradient(Rt,dt_ps,axis=0)*np.sqrt(masses)/np.sqrt(3*(N))  
Vt = np.diff(Rt,axis=0)/dt_ps*np.sqrt(masses)/np.sqrt(3*(N))


#Vt = np.loadtxt(file_trajectory)[:,1:]*np.sqrt(masses)/np.sqrt(3*N)#/(2.418884254*1e-05)
#Num_timesteps = int(len(Vt[:,0]))
#print(' Number of timesteps of simulation: ', Num_timesteps, '\n')
#tall = np.arange(Num_timesteps)*DT*2.418884254*1e-05 #conversion to picoseconds
#dt_ps = tall[1]-tall[0] 


## =============================================================================
## Decomposition
Zs = np.zeros((meta,Nqpoints))
print('Now performing decomposition... ')
for i in range(Nqpoints):
    eigvec = eigvecs[i]
    k = ks[i]
    freq_disp = freqs[i]
    print('\tkpoint:  ',k)
    
    Vcoll = np.zeros((Num_timesteps-1,15),dtype=complex)  
    for j,h,l in zip(range(15),np.repeat(range(0,N),3)*N1N2N3*3,np.tile(range(0,3),5)):
        vels = np.array(Vt[:,h+l:h+N1N2N3*3:3],dtype=complex)
        poss = R0[h:h+N1N2N3*3:3,:]
        x = np.multiply(vels,np.exp(1j*np.dot(poss,k)))
        Vcoll[:,j] = np.sum(x,axis=1)
    Tkt = Vcoll#*np.sqrt(masses)/np.sqrt(3*N)
    
    
    t, C, freq, G = corr(tall,Tkt,tau, ' ')
    Ztot = np.sqrt(np.conjugate(G)*G).real*cH/(kbH*T)
    
    print('\t\t kinetic energy of this kpoint: ',1/2*C.real[0]*cH, ' Hartree')
    print('\t\t kinetic according to eqp thm: ',1/2*kbH*T, ' Hartree')
    print('\t\t ratio: ', np.round((1/2*C.real[0]*cH)/(1/2*kbH*T)*100,2), ' %\n')
    
    Zs[:,i] = Ztot[0:meta]
## =============================================================================

np.savetxt('Zs_'+system,Zs)
np.savetxt('freq',freq[0:meta])
plot.plot_k(freq[0:meta],Zs,qpoints_scaled,freqs,title=file_eigenvectors)
