from scipy import misc
import numpy as np

def spec_nowin(T,Y,dt):
    """
    calculates the normalized spectrum of the series Y(T), with dt the sampling rate
    once removed the end-to-end line
    : in: T,Y,dt
    : out: frequencty spectrum S1(F1), with F1 the frequency
    """

    L = T.shape[0]
    #W = np.hanning(L)
    Fs = 1.0/dt # sampling frequency
    p = (Y[L-1]-Y[0])/(T[L-1]-T[0]) # end-to-end slope
    dL = p*(T-T[0])+Y[0]
    dY = Y-dL
    #print(L,p)

    freq = np.fft.rfftfreq(L, dt)
    S = np.fft.rfft(dY)/L # normalization
    #jj = np.argwhere(freq>0)
    F1 = freq#[jj]
    S1 = S#[jj]

    return F1, S1

def bandpass_nowin(T,Y,dt,Tmin,Tmax):
    """
    apply a band-pass filter (with Tmin<T<Tmax) on the series Y(T), with dt the sampling rate
    : in: T,Y,dt,Tmin,Tmax
    : out: frequencty spectrum S1(F1), with F1 the frequency
    """
    NT = T.size
    [freq, spec] = spec_nowin(T,Y,dt)
    #print(freq)
    #print(spec)
    NF = spec.shape[0]
    Tf = freq**(-1)
    j1 = np.array(np.where(Tf<Tmax))[0,:].min()
    j2 = np.array(np.where(Tf>Tmin))[0,:].max()
    #print('j1,j2=',j1,j2)
    #print(1/freq[j1],1/freq[j2])

    Sf = np.zeros((NF,), dtype=np.complex)
    Sf[:] = 0.0
    for jj in range(j1,j2):
        Sf[jj] = spec[jj]
        #Sf[NT-jj+2]=spec[NT-jj+2]
        #print(jj,Tf[jj],Tf[NT-jj])

    #print(Sf)

    Yf = np.fft.irfft(Sf,len(Y))*NT
    #print(Yf)

    return Yf


def psd_hanning(T,Y,dt):
    """
    calculates the normalized psd of the series Y(T), with dt the sampling rate
    once removed the end-to-end line and applied a hanning window
    : in: T,Y,dt
    : out: frequencty spectrum S2(F1), with F1 the frequency
    """

    L = T.shape[0]
    W = np.hanning(L)
    Fs = 1.0/dt # sampling frequency
    p = (Y[L-1]-Y[0])/(T[L-1]-T[0]) # end-to-end slope
    dL = p*(T-T[0])+Y[0]
    dY = Y-dL
    dYh = W*dY

    freq = np.fft.fftfreq(L, dt)
    S = np.fft.fft(dYh)/L # normalization
    jj = np.argwhere(freq>0)
    F1 = freq[jj]
    S1 = S[jj]
    S2=np.abs(S1)**2

    return F1, S2

def multi_tapp(T,Y,dt,Ntap):
    """
    for a series T(Y), of sampling rate dt, calculate a PSD using a
    multi-tapper method with Ntap tappers. Each tapper is applied a hanning window.
    : in: T,Y,dt, Ntap
    : out: frequencty spectrum Spec(F), with F the frequency
    """

    L = T.shape[0]
    Np=int(np.floor(L/(Ntap+1)))
    Imtam=np.linspace(Np,L-Np,Ntap)
    Nfout = int(np.floor((2*Np-1)/2))
    Spec = np.zeros((Nfout,Ntap))
    for i in range(Ntap):
        I1=int(Imtam[i])-Np+1
        I2=int(Imtam[i])+Np
        print(I1,I2)
        T1=T[I1:I2]
        Y1=Y[I1:I2]
        [F, S] = psd_hanning(T1,Y1,dt)
        Spec[:,i] = S[:,0]

    return F, Spec
