from scipy import misc
import numpy as np
from webgeodyn.constants import rE, rC
from webgeodyn.models import Models, Model
from webgeodyn.filters import time
from webgeodyn.processing import spectra
from webgeodyn.inout import s1fs2

def calc_ATA(A):

    [n,nt]=A.shape
    Am = np.mean(A,axis=1)
    dA = np.zeros((n,nt))
    for j in range(nt):
        dA[:,j] = A[:,j]-Am[:]
    ATA = np.dot(dA,dA.T)

    return ATA, Am

def calc_ATB(A,B):

    [na,nta]=A.shape
    [nb,ntb]=B.shape
    if nta != ntb:
        print("samples for matrices A and B should be the same (NTa!=NTb): stop")
        return

    Am = np.mean(A,axis=1)
    Bm = np.mean(B,axis=1)
    dA = np.zeros((na,nta))
    dB = np.zeros((nb,ntb))
    for j in range(nta):
        dA[:,j] = A[:,j]-Am[:]
        dB[:,j] = B[:,j]-Bm[:]

    ATB = np.dot(dA,dB.T)

    return ATB, Am, Bm

def lap_gnm(gnm_top_array,gnm_sub_array,r_top,r_sub,NT,lmax,eta):

    dr = r_top - r_sub
    lap_gnm = np.zeros((lmax*(lmax+2),NT))
    tmp1 = np.zeros((lmax*(lmax+2),NT))
    tmp2 = np.zeros((lmax*(lmax+2),NT))
    tmp3 = np.zeros((lmax*(lmax+2),NT))

    k=0
    for j in range(lmax):
        l=j+1
        for m in range (2*l+1):
            tmp1[k,:] = 2/dr**2 * (gnm_sub_array[k,:]-gnm_top_array[k,:])
            tmp2[k,:] = - 2*(l+1)/r_top*(1/r_top+1/dr) * gnm_top_array[k,:]
            tmp3[k,:] =  - l*(l+1)/r_top**2 * gnm_top_array[k,:]
            lap_gnm[k,:] = tmp1[k,:]+tmp2[k,:]+tmp3[k,:]
            k=k+1

    lap_gnm[:,:] = eta * lap_gnm[:,:]

    print(np.mean(tmp1[0:5,:],axis=1))
    print(np.mean(tmp2[0:5,:],axis=1))
    print(np.mean(tmp3[0:5,:],axis=1))
    print(np.mean(lap_gnm[0:5,:],axis=1))

    return lap_gnm

def calc_diffusion_matrices(file_format,data_file_top,data_file_sub,r_top,r_sub,Tcut,LcutU,LcutB):

    model_adim= Model(data_file_top,file_format)
    model_dim_top = s1fs2.num2dim_S1fs2(model_adim)

    model_adim= Model(data_file_sub,file_format)
    model_dim_sub = s1fs2.num2dim_S1fs2(model_adim)

    lb = model_dim_top.measures["MF"].lmax
    NT = model_dim_top.times.shape[0]

    B_top = model_dim_top.measures['MF'].data.T
    B_sub = model_dim_sub.measures['MF'].data.T

    r_top = rC

    lap_B = lap_gnm(B_top,B_sub,r_top,r_sub,NT,lb) # output in nT/ km^2

    print('careful ! scaling of eta...')
    eta = 1.0 # in m^2/s
    eta = eta * year2sec *10**6 # in km^2/yr
    D = eta*lap_B
    [DTD, Dm] = calc_ATA(D)

    return DTD,Dm

def calc_diffusion(file_format,data_file_top,data_file_sub,r_top,r_sub,LcutU,LcutB,Tcut):

    # model top
    model_adim= Model(data_file_top,file_format)
    [model_dim_top, fac_T, fac_B, fac_L] = s1fs2.num2dim_S1fs2(model_adim)

    model_top_trunc = model_dim_top.copy()
    model_top_trunc.measures["U"].truncate(LcutU)
    model_top_trunc.measures["MF"].truncate(LcutB)

    lb = model_top_trunc.measures["MF"].lmax
    NT = model_top_trunc.times.shape[0]

    # model sub
    model_adim= Model(data_file_sub,file_format)

    model_sub_trunc = model_adim.copy()
    model_sub_trunc.measures["U"].truncate(LcutU)
    model_sub_trunc.measures["MF"].truncate(LcutB)
    model_sub_trunc.measures["U"].data = model_sub_trunc.measures["U"].data * fac_L/fac_T
    model_sub_trunc.measures["MF"].data = model_sub_trunc.measures["MF"].data * fac_B
    model_sub_trunc.times = (model_sub_trunc.times-model_sub_trunc.times[0]) * fac_T

    dt_dim = model_top_trunc.times[1]-model_top_trunc.times[0]
    print("dt (yrs)=",dt_dim)
    fs=1/dt_dim
    print("fs (yr^-1)=",fs)

    order = 4
    print("cut-off period (yrs)=",Tcut)
    Wn = 1./Tcut #yr^-1

    model_top_hp = time.butterworth(model_top_trunc,'highpass',fs,order,Wn,copy=True)
    model_sub_hp = time.butterworth(model_sub_trunc,'highpass',fs,order,Wn,copy=True)

    model_top_lp = time.butterworth(model_top_trunc,'lowpass',fs,order,Wn,copy=True)
    model_sub_lp = time.butterworth(model_sub_trunc,'lowpass',fs,order,Wn,copy=True)

    B_top_hp = model_top_hp.measures['MF'].data.T
    B_sub_hp = model_sub_hp.measures['MF'].data.T
    B_top_lp = model_top_lp.measures['MF'].data.T
    B_sub_lp = model_sub_lp.measures['MF'].data.T

    Pm=0.2
    eta = 1/Pm * fac_L**2 / fac_T # in km^2/yr
    D_B_hp = lap_gnm(B_top_hp,B_sub_hp,r_top,r_sub,NT,lb,eta) # in nT/yr
    D_B_lp = lap_gnm(B_top_lp,B_sub_lp,r_top,r_sub,NT,lb,eta) # in nT/yr

    return D_hp, D_lp

def calc_prior_matrices(file_format,data_file,Tcut,LcutU,LcutB):

    model_adim= Model(data_file,file_format)
    model_dim = s1fs2.num2dim_S1fs2(model_adim)

    time_dim = model_dim.times
    dt_dim = time_dim[1]-time_dim[0]

    print("dt (yrs)=",dt_dim)
    fs=1/dt_dim
    print("fs (yr^-1)=",fs)

    order = 4
    Tcut = 100. # yrs
    print("cut-off period (yrs)=",Tcut)
    Wn = 1./Tcut #yr^-1

    model_dim_lp = time.butterworth(model_dim,'lowpass',fs,order,Wn,copy=True)
    model_dim_hp = time.butterworth(model_dim,'highpass',fs,order,Wn,copy=True)

    model_dim_hp_cut = model_dim_hp.copy()
    model_dim_hp_cut.measures["U"].truncate(LcutU)
    model_dim_hp_cut.measures["MF"].truncate(LcutB)

    model_dim_lp_cut = model_dim_lp.copy()
    model_dim_lp_cut.measures["U"].truncate(LcutU)
    model_dim_lp_cut.measures["MF"].truncate(LcutB)

    Uhp = model_dim_hp_cut.measures['U'].data.T
    [UTUhp, Umhp] = calc_ATA(Uhp)

    Ulp = model_dim_lp_cut.measures['U'].data.T
    [UTUlp, Umlp] = calc_ATA(Ulp)

    Bhp = model_dim_hp_cut.measures['MF'].data.T
    [BTBhp, Bmhp] = calc_ATA(Bhp)

    Blp = model_dim_lp_cut.measures['MF'].data.T
    [BTBlp, Bmlp] = calc_ATA(Blp)

    prior_dict = {
        "UTUhp" : UTUhp,
        "Umhp" : Umhp,
        "UTUlp" : UTUlp,
        "Umlp" : Umlp,
        "BTBhp" : BTBhp,
        "Bmhp" : Bmhp,
        "BTBlp" : BTBlp,
        "Bmlp" : Bmlp
    }

    return prior_dict
