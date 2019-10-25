# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 11:05:28 2018

@author: Gabriele Coiana
"""

import numpy as np
import yaml
yaml.warnings({'YAMLLoadWarning': False})


def read_parameters():
    """
    This function takes the input parameters from the file input.txt 
    and applies the right types to the variables
    """
    lista = []
    f = open('input', 'r')
    A = f.readlines()
    for string in A:
        index = string.find('=')+2
        lista.append(string[index:-1])
        
    lattice_param = float(lista[1])
    
    m = lista[2]
    masses = np.fromstring(m, dtype=np.float, sep=',')
    mba,mti,mo = masses[0],masses[1],masses[2]
    
    N = lista[3]
    n = np.fromstring(N, dtype=np.int, sep=',')
    N1,N2,N3 = n[0],n[1],n[2]
    
    band = lista[4]
    a = np.fromstring(band, dtype=np.float, sep=',')
    num = len(a)/3
    ks = np.split(a,num)
    
    file_eigenvectors = str(lista[5])
    
    file_trajectory = str(lista[6])
    
    file_initial_conf = str(lista[7])
    
    system = str(lista[8])
    
    DT = float(lista[9])
    tau = int(lista[10])
    
    T = float(lista[11])
    
    f.close()
    return lattice_param, mba,mti,mo, N1,N2,N3, ks, file_eigenvectors, file_trajectory, file_initial_conf, system, DT, tau, T




def read_phonopy(file_eigenvectors):
    ## =============================================================================
    # Phonopy frequencies and eigenvectors
    data = yaml.load(open(file_eigenvectors))
    #D = data['phonon'][0]['dynamical_matrix']
    #D = np.array(D)
    #D_real, D_imag = D[:,0::2], 1j*D[:,1::2]
    #D = (D_real + D_imag)*21.49068**2#*0.964*10**(4)#
    
    data2 = data['phonon']
    qpoints_scaled = []
    freqs = []
    eigvecs = []
    for element in data2:
        qpoints_scaled.append(element['q-position'])
        freq = []
        eigvec = np.zeros((15,15),dtype=complex)
        for j in range(len(element['band'])):
            branch = element['band'][j]
            freq.append(branch['frequency'])
            
            eigen = np.array(branch['eigenvector'],dtype=complex)
            eigen_real = eigen[:,:,0]
            eigen_imag = eigen[:,:,1]
            eigen = eigen_real + 1j*eigen_imag
            eigen = eigen.reshape(15,)
            eigvec[:,j] = eigen
    
        freqs.append(freq)
        eigvecs.append(eigvec)
    qpoints_scaled = np.array(qpoints_scaled)
    freqs = np.array(freqs)
    Nqpoints = len(qpoints_scaled[:,0])
    
    
    c = 1.88973 #conversion to Bohrs
    Hk = np.array(data['reciprocal_lattice'])*2*np.pi*1/c
    ks = np.dot(Hk,qpoints_scaled.T).T
    # =============================================================================
    return Nqpoints, qpoints_scaled, ks, freqs, eigvecs







