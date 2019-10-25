#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 15:11:33 2019

@author: Gabriele Coiana
"""
import numpy as np
from decomp import cell, read, plot
import os

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
            d = c
        else:
            d = np.sum(c)
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
    R0 = np.loadtxt('R0')                       #rhombo R0
    R0 = np.repeat(R0,3,axis=0)
if (system=='avg'):
    R0 = np.loadtxt('R0_avg')


Rt = np.loadtxt(file_trajectory)[:,1:]
Num_timesteps = int(len(Rt[:,0]))
print(' Number of timesteps of simulation: ', Num_timesteps, '\n')
tall = np.arange(Num_timesteps)*DT*2.418884254*1e-05 #conversion to picoseconds
dt_ps = tall[1]-tall[0]
meta = int(Num_timesteps/2)
##Vt = np.gradient(Rt,dt_ps,axis=0)  
Vt = np.diff(Rt,axis=0)/dt_ps*np.sqrt(masses)/np.sqrt(3*(N))
    
#Vt = np.loadtxt(file_trajectory)[:,1:]*np.sqrt(masses)/np.sqrt(3*N)#/(2.418884254*1e-05)
#Num_timesteps = int(len(Vt[:,0]))
#print(' Number of timesteps of simulation: ', Num_timesteps, '\n')
#tall = np.arange(Num_timesteps)*DT*2.418884254*1e-05 #conversion to picoseconds
#dt_ps = tall[1]-tall[0]

t_tot, C_tot, freq_tot, G_tot = corr(tall,Vt,tau, ' ')
print(' Average total kinetic energy per dof: ', 1/2*C_tot[0]*cH, ' Hartree')
print(' Kinetic energy per dof according to eqp thm: ', 1/2*kbH*T, ' Hartree')
print('\t\t ratio: ', np.round((1/2*C_tot[0]*cH)/(1/2*kbH*T)*100,2), ' %\n')

print(' Done. Performing decomposition...\n')

flag = ''
try:
    namedir = 'phonDOS_'+system
    os.mkdir(namedir)
    flag = 'created'
except FileExistsError:
    if(flag=='created'):
        bbb = 1
    else:
        number_of_folders = len(np.sort([x[1] for x in os.walk('.')][0]))
        print('Folder '+namedir+' already exists. Creating phonDOS_'+str(system)+'_'+str(number_of_folders))
        namedir = namedir+'_'+str(number_of_folders)
        os.mkdir(namedir)
anis = list(range(15))
for i in range(Nqpoints):
    eigvec = eigvecs[i]
    freq_disp = freqs[i]
    k = ks[i]
    print('\t kpoint ',k)

    Vcoll = np.zeros((Num_timesteps-1,15),dtype=complex)  
    for j,h,l in zip(range(15),np.repeat(range(0,N),3)*N1N2N3*3,np.tile(range(0,3),5)):
        vels = np.array(Vt[:,h+l:h+N1N2N3*3:3],dtype=complex)
        poss = R0[h:h+N1N2N3*3:3,:]
        x = np.multiply(vels,np.exp(1j*np.dot(poss,k)))
        Vcoll[:,j] = np.sum(x,axis=1)
    Tkt = Vcoll#*np.sqrt(masses)/np.sqrt(3*N)
    
    #eigvec_exp = np.array([0,0,0,0,0,0.5,0,0,-0.9,0,0,-0.6,0,0,0.6])
    #a = np.array([0,0,1,0,0,-1,0,0,-1,0,0,-1,0,0,-1])
    eigvecH = np.conjugate(eigvec.T)
    
    Qkt = np.dot(eigvecH,Tkt.T).T#.reshape(Num_timesteps,1)
    
    t, C, freq, G = corr(tall,Tkt,tau, ' ')
    Ztot = np.sqrt(np.conjugate(G)*G).real*cev
    print('\t\t kinetic energy of this kpoint: ',1/2*C.real[0]*cH, ' Hartree')
    print('\t\t kinetic according to eqp thm: ',1/2*kbH*T, ' Hartree')
    print('\t\t ratio: ', np.round((1/2*C.real[0]*cH)/(1/2*kbH*T)*100,2), ' %')
    
    
    t_proj, C_proj, freq_proj, G_proj = corr(tall,Qkt,tau, 'projected')
    Z = np.sqrt(np.conjugate(G_proj)*G_proj).real*cev
#    print('\t\t sum of projected: ',1/2*np.sum(C_proj[0].real)*cH, ' Hartree')

    meta = int(len(t)/2)
    
    for n in range(15):
        #plot.plot(freq[0:meta],Z[0:meta],'Spectrum of '+str(k))
        #anis[n] = plot.plot_with_ani(freq[0:meta],Z[0:meta,n],Ztot[0:meta], k, eigvec[:,n],freq_disp[n],n,file_eigenvectors,masses,10)
        plot.save_proj(freq[0:meta],Z[0:meta,n],Ztot[0:meta], qpoints_scaled[i], eigvec[:,n],freq_disp[n],n,namedir,np.repeat([mba, mti, mo, mo, mo],3))
    
    print()






