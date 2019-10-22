#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 13 14:12:07 2019

@author: gc4217
"""
import numpy as np
import os, sys

def avg_vs_t(time,quantity):
    avg = []
    for i in range(1,len(time)):
        dt = time[i]-time[i-1]
        y = quantity[0:i]
        integral = np.sum(dt*y,axis=0)
        avg.append(1/(i*dt)*integral)
    avg = np.array(avg)
    return avg

N1, N2, N3 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
N1N2N3 = N1*N2*N3
N = N1*N2*N3*5

print('Hello, Im now converting the ASAP output files...\n')

with open('Cartesian_M0','r') as f:
    A = f.readlines()[0:N+1]
del A[0]


with open('pos','w') as g:
    g.writelines(A)
    
R0 = np.loadtxt('pos',usecols=(1,2,3))
np.savetxt('R0',R0)

os.remove('pos')

print('Finished. data_pos and runn_avg_pos created.\n\n')
print('Please copy the file data_pos to your phonon DOS folder!')




























