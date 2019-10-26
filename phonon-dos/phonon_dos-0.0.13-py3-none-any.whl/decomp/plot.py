#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 13:56:19 2019

@author: gabriele
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation
import numpy as np
import os

def animate(frame_BaTiO3,plotBa,plotTi,plotO,plotBaimag,plotTiimag,plotOimag):
    plotBa.collections = []
    plotTi.collections = []
    plotO.collections = []
    Bai, Tii, Oi = frame_BaTiO3[0:8*3], frame_BaTiO3[8*3:9*3], frame_BaTiO3[9*3::]
    Baiimag, Tiiimag, Oiimag = frame_BaTiO3[0:8*3], frame_BaTiO3[8*3:9*3], frame_BaTiO3[9*3::]
    plotBa._offsets3d = (Bai[0::3],Bai[1::3],Bai[2::3])
    plotTi._offsets3d = (Tii[0::3],Tii[1::3],Tii[2::3])
    plotO._offsets3d = (Oi[0::3],Oi[1::3],Oi[2::3])
#    plotBaimag._offsets3d = (Baiimag[0::3],Baiimag[1::3],Baiimag[2::3])
#    plotTiimag._offsets3d = (Tiiimag[0::3],Tiiimag[1::3],Tiiimag[2::3])
#    plotOimag._offsets3d = (Oiimag[0::3],Oiimag[1::3],Oiimag[2::3])
    return

def plot_eigvec(ax,k,eigvec,freq, fig):
    t = np.arange(0,100,1)
    
    Ruc = np.array([[0,0,0],[8,0,0],[0,8,0],[8,8,0],[0,0,8],[8,0,8],[0,8,8],[8,8,8],[4,4,4],[4,4,0],[4,4,8],[4,0,4],[4,8,4],[0,4,4],[8,4,4]])
    Rucxyz = np.repeat(Ruc,3,axis=0)
    
    eig1 = np.tile(eigvec[0:3],8)
    eig2 = np.tile(eigvec[3:6],1)
    eig3 = np.tile(eigvec[6:9],2)
    eig4 = np.tile(eigvec[9:12],2)
    eig5 = np.tile(eigvec[12::],2)
    
    
    EIGs = np.hstack((eig1,eig2,eig3,eig4,eig5))
    
    
    exp1 = np.exp(1j*np.sum(np.multiply(k,Rucxyz),axis=1))
    #exp2 = np.exp(1j*freq*t).reshape(1,len(t))
    exp2 = np.sin(t).reshape(1,len(t))
    EIG_exp = np.multiply(EIGs,exp1)
    ut = np.dot(EIG_exp.reshape(len(EIGs),1),exp2)
    
    #print(np.max(np.imag(ut)))
    
    Rt = Ruc.flatten().reshape(len(EIGs),1) + np.real(ut)
    Rt2 = Ruc.flatten().reshape(len(EIGs),1) + np.imag(ut)
    
    Ba, Ti, O = np.real(Rt[0:8*3,:]), np.real(Rt[8*3:9*3,:]), np.real(Rt[9*3::,:])
    Baimag, Tiimag, Oimag = Rt2[0:8*3,:], Rt2[8*3:9*3,:], Rt2[9*3::,:]

    
    plotBa = ax.scatter(Ba[0::3,0],Ba[1::3,0],Ba[2::3,0],s=137*50/10)
    plotTi = ax.scatter(Ti[0::3,0],Ti[1::3,0],Ti[2::3,0],s=47*50/10)
    plotO = ax.scatter(O[0::3,0],O[1::3,0],O[2::3,0],s=15*50/10)
#    fig2 = plt.figure()
#    ax2 = fig2.add_subplot(111,projection='3d')
#    plotBaimag = ax2.scatter(Baimag[0::3,0],Baimag[1::3,0],Baimag[2::3,0],s=137*50)
#    plotTiimag = ax2.scatter(Tiimag[0::3,0],Tiimag[1::3,0],Tiimag[2::3,0],s=47*50)
#    plotOimag = ax2.scatter(Oimag[0::3,0],Oimag[1::3,0],Oimag[2::3,0],s=15*50)
    ani = animation.FuncAnimation(fig,animate,frames=Rt.T,fargs=(plotBa,plotTi,plotO,1,1,1))
    return ani

def plot(x,y,title):
    fig,ax = plt.subplots()
    ax.plot(x,y)
    ax.set_xlabel('Frequency [Thz]')
    ax.set_title(title)
    plt.show()
    return

def plot_eigvec_noani(ax,k,eigvec,freq, fig):
    t = np.arange(0,100,1)
    
    Ruc = np.array([[0,0,0],[8,0,0],[0,8,0],[8,8,0],[0,0,8],[8,0,8],[0,8,8],[8,8,8],[4,4,4],[4,4,0],[4,4,8],[4,0,4],[4,8,4],[0,4,4],[8,4,4]])
    Rucxyz = np.repeat(Ruc,3,axis=0)
    
    eig1 = np.tile(eigvec[0:3],8)
    eig2 = np.tile(eigvec[3:6],1)
    eig3 = np.tile(eigvec[6:9],2)
    eig4 = np.tile(eigvec[9:12],2)
    eig5 = np.tile(eigvec[12::],2)
    
    
    EIGs = np.hstack((eig1,eig2,eig3,eig4,eig5))
    
    
    exp1 = np.exp(1j*np.sum(np.multiply(k,Rucxyz),axis=1))
    #exp2 = np.exp(1j*freq*t).reshape(1,len(t))
    exp2 = np.sin(t).reshape(1,len(t))
    EIG_exp = np.multiply(EIGs,exp1)
    ut = np.dot(EIG_exp.reshape(len(EIGs),1),exp2)
    
    #print(np.max(np.imag(ut)))
    
    Rt = Ruc.flatten().reshape(len(EIGs),1) + np.real(ut)
    Rt2 = Ruc.flatten().reshape(len(EIGs),1) + np.imag(ut)
    
    Ba, Ti, O = np.real(Rt[0:8*3,:]), np.real(Rt[8*3:9*3,:]), np.real(Rt[9*3::,:])
    O1 = np.real(Rt[9*3:11*3,:])
    O2 = np.real(Rt[11*3:13*3,:])
    O3 = np.real(Rt[13*3:15*3,:])
    Baimag, Tiimag, Oimag = Rt2[0:8*3,:], Rt2[8*3:9*3,:], Rt2[9*3::,:]

    
    plotBa = ax.scatter(Ba[0::3,0],Ba[1::3,0],Ba[2::3,0],s=137*50/10,alpha=0.1)
    plotTi = ax.scatter(Ti[0::3,0],Ti[1::3,0],Ti[2::3,0],s=47*50/10,alpha=0.1)
    plotO = ax.scatter(O[0::3,0],O[1::3,0],O[2::3,0],s=15*50/10,alpha=0.1)
    ax.quiver(Ba[0::3,0],Ba[1::3,0],Ba[2::3,0],eigvec[0],eigvec[1],eigvec[2],linewidth=0.8,color=plt.cm.coolwarm(eigvec[0:3].real))
    ax.quiver(Ti[0::3,0],Ti[1::3,0],Ti[2::3,0],eigvec[3],eigvec[4],eigvec[5],linewidth=0.8,color=plt.cm.coolwarm(eigvec[3:6].real))#,color='r')
    ax.quiver(O1[0::3,0],O1[1::3,0],O1[2::3,0],eigvec[6],eigvec[7],eigvec[8],linewidth=0.8,color=plt.cm.coolwarm(eigvec[6:9].real))#,color='green')
    ax.quiver(O2[0::3,0],O2[1::3,0],O2[2::3,0],eigvec[9],eigvec[10],eigvec[11],linewidth=0.8,color=plt.cm.coolwarm(eigvec[9:12].real))#,color='green')
    ax.quiver(O3[0::3,0],O3[1::3,0],O3[2::3,0],eigvec[12],eigvec[13],eigvec[14],linewidth=0.8,color=plt.cm.coolwarm(eigvec[12::].real))#,color='green')
    
    
    
#    fig2 = plt.figure()
#    ax2 = fig2.add_subplot(111,projection='3d')
#    plotBaimag = ax2.scatter(Baimag[0::3,0],Baimag[1::3,0],Baimag[2::3,0],s=137*50)
#    plotTiimag = ax2.scatter(Tiimag[0::3,0],Tiimag[1::3,0],Tiimag[2::3,0],s=47*50)
#    plotOimag = ax2.scatter(Oimag[0::3,0],Oimag[1::3,0],Oimag[2::3,0],s=15*50)
    return 

def plot_with_ani(x,y,ytot, k,eigvec,freq,n,eigname,masses,ampl):
    fig,ax = plt.subplots()
    graph1, = ax.plot(x,y,label='mode-projected DOS')
    graph2, = ax.plot(x,ytot,'--',label='total DOS')
    ax.set_xlabel('Frequency [Thz]')
    ax.set_title('Spectrum of mode n. '+str(n)+' kpoint '+str(k))
    
    ax1 = ax.twiny()
    ax1.set_xlabel('Frequency [cm$^{-1}$]')
    ax1.plot(x*33.35641,-np.ones(len(x)),c='white',linewidth=0,label='')
    
    
    graph3, = ax.plot(np.repeat(freq,100),np.linspace(0,ytot.max(),100),':' ,c='r', label='freq from dispersion')
    plt.legend(handles=[graph1, graph2, graph3], loc=2)
    
    
    ax2 = fig.add_axes([0.5, .5, .3, .3],projection='3d')
    ax2.set_title(str(eigname)+'\nfrequency: '+str(freq))
    eigvec = eigvec/np.sqrt(masses)*ampl
    ani = plot_eigvec(ax2,[0,0,0],eigvec,freq,fig)
    
    
    print('Mode frequency: ', freq, '\n')
    print('Eigenvector components:')
    print(np.round(np.reshape(np.real(eigvec),(5,3)),2))
    print()
    print('Imaginary part:')
    print(np.round(np.reshape(np.imag(eigvec),(5,3)),2))
    print()
    
    plt.show()
    return ani

def save_proj(x,y,ytot, k,eigvec,freq,n,namedir,masses):
    plt.ioff()
    fig,ax = plt.subplots()
    graph1, = ax.plot(x,y,label='mode-projected DOS')
    graph2, = ax.plot(x,ytot,'--',label='total DOS')
    ax.set_xlabel('Frequency [Thz]')
    ax.set_ylabel('DOS [ev * ps]')
    fig.suptitle('Spectrum of mode n. '+str(n)+' kpoint '+str(k))
    
    ax1 = ax.twiny()
    ax1.set_xlabel('Frequency [cm$^{-1}$]')
    ax1.plot(x*33.35641,-np.ones(len(x)),c='white',linewidth=0,label='')
    ax1.set_xlim(-1*33.35641,30*33.35641)
    
    
    graph3, = ax.plot(np.repeat(freq,100),np.linspace(0,ytot.max(),100),':' ,c='r', label='freq from dispersion')
    #graph3, = ax.axvline(x=freq,  ymin=0.05, ymax=1, c='blue',linestyle=':', label='freq from dispersion')
#    print('Mode frequency: ', freq, '\n')
#    print('Eigenvector components:')
#    print(np.round(np.reshape(np.real(eigvec),(5,3)),2))
#    print()
#    print('Imaginary part:')
#    print(np.round(np.reshape(np.imag(eigvec),(5,3)),2))
#    print()
#    print()
    name_current_dir = namedir+'/'+str(k)
    try:
        os.mkdir(name_current_dir)
        
    except FileExistsError:
        a = 1
    ax.set_ylim(bottom=-np.max(ytot)/10)#,top=30000)
    ax.set_xlim(left=-1,right=30)
    plt.legend(handles=[graph1, graph2, graph3])
    plt.subplots_adjust(top=0.85)
    
    if(np.allclose(k,[0,0,0])):
        ax2 = fig.add_axes([0.7, 0.4, .2, .2],projection='3d')
        ax2.set_xticks([])
        ax2.set_yticks([])
        ax2.set_zticks([])
        #ax2.xticks([])
    #    ax2.set_title('frequency: '+str(freq))
        ampl = 30
        eigvec = eigvec/np.sqrt(masses)*ampl
        ggraph = plot_eigvec_noani(ax2,[0,0,0],eigvec,freq,fig)
    
    fig.savefig(name_current_dir+'/proj_'+str(k)+'mode'+str(n)+'.pdf')
    plt.close(fig)
    return 
    
def plot_k(f, data, indexes,freqs, title=''):
    """
    Plotting the dispersion from MD and from phonon theory.
    
    Variables:
        f = array of the frequencies [Thz] 
        data = matrix with spectra from all k points: shape = (timesteps,N)
        indexes = list of all kpoints
        freqs = frequencies from phonopy
    """
    fig,ax = plt.subplots()
    plt.suptitle('Spectrum via MD and phonon theory')
    #ax.set_title(title)
    ax.set_ylabel('[Thz]')
    N = len(data[0,:])
    offset = np.zeros(N) + f[0]
    df = f[1]-f[0]
    k = np.linspace(0,1,N)
    dk = k[1] - k[0]
    

    norm = [plt.cm.colors.Normalize(vmax=abs(data[0::1,l]).max(), vmin=-abs(data[0::1,l]).min()) for l in range(len(data[0,:]))]
    
    for j in range(len(data[0::1,0])):
        ax.bar(k, np.repeat(df,N), bottom=offset-df/2,  color=plt.cm.Blues(norm[0](data[j,:])), tick_label=indexes, align='center', width=dk, alpha=None)
        offset = offset + df
        
    ax2 = plt.twinx()
    ax2.set_ylabel('[Thz]')
    for j in range(14):
        ax2.scatter(k,freqs[:,j], c='b', marker='x', s=100)
    ax2.scatter(k,freqs[:,14], c='b', marker='x', s=100, label='freq from dispersion')
    
        
    ax2.get_shared_y_axes().join(ax, ax2)
    plt.ylim([f[0], f[-1]])
    plt.legend()
    plt.show()
    return
    









































def corr_j(tcorr,X,dt,masses):
    Nsteps = len(tcorr)
    N = np.size(X[0])
    sigma2 = np.var(X,axis=0)
    C = []
    for i in range(Nsteps):
        X_i = X[i::,:]
        Xjj = np.concatenate((X[i::,:],X[0:i,:]))#[i::,:]
        a = np.multiply(np.conjugate(X),Xjj)
        b = 1/(Nsteps) * np.sum(a,axis=0)#/sigma2
        c = np.multiply(b,masses)
        d = 1/N*np.sum(c)
        C.append(d)
    C = np.array(C)
    freq = np.fft.fftfreq(Nsteps,d=dt)
    Z = np.fft.fft(C,axis=0)
    return C, freq, Z

def corr_jaa(tall,X,dt,masses):
    M = len(tall)
    tau = 1000
    tmax = M - tau
    t = np.arange(0,tau)*dt
    N = np.size(X[0])   
    X0 = X[0:tau,:]
    C = []
    for n in range(tau):
        A = []
        for m in range(tmax):
            xj = X[m,:]
            xjj = X[m+n,:]
            a = np.multiply(xj,xjj)
            A.append(a*masses)
        A = np.array(A)
        Cn = np.average(A,axis=0)
        C.append(np.average(Cn))
    C = np.array(C)
    freq = np.fft.fftfreq(tau,d=dt)
    Z = np.fft.fft(C,axis=0)
    return t, C, freq, Z
    
    
    
    
    
    
    
