# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

from scipy.signal import fftconvolve
from math import ceil
from math import sqrt


def mother(family):
    """ 
    Derived from base coefficient values stated in: 
    
    I. Daubechies, Ten lectures on wavelets, CBMS, SIAM, 61, 1994, 194-202.
    
    """

    if family=="daubechies1" or family == "db1":
        base = [ 0.5, 0.5]
    
    elif family=="daubechies2" or family == "db2":
        base = [ 0.341506350946220,   0.591506350945870,   
                 0.158493649053780,  -0.091506350945870]
    
    elif family=="daubechies3" or family == "db3":
        base = [ 0.235233603892700,   0.570558457917310,   0.325182500263710,  
                -0.095467207784260,  -0.060416104155350,   0.024908749865890]

    elif family=="daubechies4" or family == "db4":
        base = [  0.162901714025620,   0.505472857545650,   0.446100069123190,  -0.019787513117910,  -0.132253583684370,
                  0.021808150237390,   0.023251800535560,  -0.007493494665130]

    elif family=="daubechies5" or family == "db5":
        base = [ 0.113209491291730,   0.426971771352710,   0.512163472130160,   0.097883480673750,  -0.171328357691330,
                -0.022800565942050,   0.054851329321080,  -0.004413400054330,  -0.008895935050930,   0.002358713969200]

    elif family=="daubechies6" or family == "db6":
        base = [ 0.078871216001430,   0.349751907037570,   0.531131879941210,   0.222915661465050,  -0.159993299445870,
                -0.091759032030030,   0.068944046487200,   0.019461604853960,  -0.022331874165480,   0.000391625576030,
                 0.003378031181510,  -0.000761766902580]

    elif family=="daubechies7" or family == "db7":
        base = [ 0.055049715372850,   0.280395641813040,   0.515574245818330,   0.332186241105660,  -0.101756911231730,
                -0.158417505640540,   0.050423232504850,   0.057001722579860,  -0.026891226294860,  -0.011719970782350,
                 0.008874896189620,   0.000303757497760,  -0.001273952359060,   0.000250113426580]

    elif family=="daubechies8" or family == "db8":
        base = [ 0.038477811054060,   0.221233623576240,   0.477743075214380,   0.413908266211660,  -0.011192867666650,
                -0.200829316391110,   0.000334097046280,   0.091038178423450,  -0.012281950523000,  -0.031175103325330,
                 0.009886079648080,   0.006184422409540,  -0.003443859628130,  -0.000277002274210,   0.000477614855330,
                -0.000083068630600 ]

    elif family=="coiflet1" or family=="coif1":
        
        base = [  0.500000000000000,   0.500000000000000  ]

    elif family=="coiflet2" or family=="coif2":
        
        base = [  0.011587596739000,  -0.029320137980000,  -0.047639590310000,   0.273021046535000,   0.574682393857000,
                  0.294867193696000,  -0.054085607092000,  -0.042026480461000,   0.016744410163000,   0.003967883613000,
                 -0.001289203356000,  -0.000509505399000  ]
    
    elif family=="coiflet3" or family=="coif3":
        
        base = [ -0.002682418671000,   0.005503126709000,   0.016583560479000,  -0.046507764479000,  -0.043220763560000,
                  0.286503335274000,   0.561285256870000,   0.302983571773000,  -0.050770140755000,  -0.058196250762000,
                  0.024434094321000,   0.011229240962000,  -0.006369601011000,  -0.001820458916000,   0.000790205101000,
                  0.000329665174000,  -0.000050192775000,  -0.000024465734000  ]

    elif family=="coiflet4" or family=="coif4":
        
        base = [  0.000630961046000,  -0.001152224852000,  -0.005194524026000,   0.011362459244000,   0.018867235378000,
                 -0.057464234429000,  -0.039652648517000,   0.293667390895000,   0.553126452562000,   0.307157326198000,
                 -0.047112738865000,  -0.068038127051000,   0.027813640153000,   0.017735837438000,  -0.010756318517000,
                 -0.004001012886000,   0.002652665946000,   0.000895594529000,  -0.000416500571000,  -0.000183829769000,
                  0.000044080354000,   0.000022082857000,  -0.000002304942000,  -0.000001262175000 ]

    elif family=="coiflet5" or family=="coif5":
        
        base = [ -0.000149963800000,   0.000253561200000,   0.001540245700000,  -0.002941110800000,  -0.007163781900000,
                  0.016552066400000,   0.019917804300000,  -0.064997262800000,  -0.036800073600000,   0.298092323500000,
                  0.547505429400000,   0.309706849000000,  -0.043866050800000,  -0.074652238900000,   0.029195879500000,
                  0.023110777000000,  -0.013973687900000,  -0.006480090000000,   0.004783001400000,   0.001720654700000,
                 -0.001175822200000,  -0.000451227000000,   0.000213729800000,   0.000099377600000,  -0.000029232100000,
                 -0.000015072000000,   0.000002640800000,   0.000001459300000,  -0.000000118400000,  -0.000000067300000 ]

    elif family=="symlet1" or family=="sym1":
        
        base = [  0.500000000000000,   0.500000000000000  ]

    elif family=="symlet2" or family=="sym2":
        
        base = [   0.341506350946220,   0.591506350945870,   0.158493649053780,  -0.091506350945870,  ]

    elif family=="symlet3" or family=="sym3":
        
        base = [  0.235233603892700,   0.570558457917310,   0.325182500263710,  
                 -0.095467207784260,  -0.060416104155350,   0.024908749865890]

    elif family=="symlet4" or family=="sym4":
        
        base = [  0.022785172948000,  -0.008912350720850,  -0.070158812089500,   0.210617267102000,   0.568329121705000,
                  0.351869534328000,  -0.020955482562550,  -0.053574450709000, ]

    elif family=="symlet5" or family=="sym5":
        
        base = [  0.013816076478930,  -0.014921249934380,  -0.123975681306750,   0.011739461568070,   0.448290824190920,
                  0.511526483446050,   0.140995348427290,  -0.027672093058360,   0.020873432210790,   0.019327397977440 ]

    elif family=="symlet6" or family=="sym6":
        
        base = [ -0.005515933754690,   0.001249961046390,   0.031625281329940,  -0.014891875649220,  -0.051362484930900,
                  0.238952185666050,   0.556946391963960,   0.347228986478350,  -0.034161560793240,  -0.083431607705840,
                  0.002468306185920,   0.010892350163280 ]
    
    else:
        raise ValueError('could not find wavelet family = %s' % (family,))
    
    base = np.array(base)
    euclid_norm = np.sqrt(np.sum(base*base))
    
    base = base/euclid_norm
    
    low_forward  = np.array([item for item in base[::-1]])
    low_reverse  = np.array([item for item in base])
    high_forward = np.array([item * (2*(i%2)-1) for i,item in enumerate(base)])
    high_reverse = np.array([item * (1-2*(i%2)) for i,item in enumerate(base[::-1])])
    
    return low_forward, high_forward, low_reverse, high_reverse



def dwt1(data, wavelet):

    lo, hi, _, _ = mother(wavelet)
    
    npad = int(len(lo)/2 + len(hi)/2)
    
    # Apply periodic extension to data as needed
    # - ensure even number of points
    # - pad with periodic data
    data = np.append(data,data[-1]) if len(data)%2 else data 
    data = np.pad(data, (int(npad/2),int(npad/2)), 'wrap')    

    # Filter data to get approx and detail coefficients
    ca = np.real(fftconvolve(data, lo))
    cd = np.real(fftconvolve(data, hi))

    # Extract from extended array and down sample by 2
    ca = ca[npad:-npad:2].copy()      
    cd = cd[npad:-npad:2].copy()
    
    return ca,cd


def dwt(data, levels, wavelet):
    """
    Assumes that we deal with data wrap as a periodic function
    
    """
    alerts = np.array([])
    coeffs = np.array([])
    widths = np.array([])
    
    lmax   = int(np.ceil(np.log2(len(data))))-2 
    levels = levels if levels < lmax else lmax 
    
    # Ensure data is even length
    if len(data)%2 != 0:
        data   = np.append(data, data[-1])
        alerts = np.append(alerts, 1)
    else:
        alerts = np.append(alerts, 0)

    widths = np.append(widths, len(data))
    alerts = np.append(alerts, levels)
    alerts = np.append(alerts, 0)
        
    orig = data

    # Iterate through levels applying wavelet filter
    
    for level in range(levels):
        ca,cd   = dwt1(orig, wavelet)
        coeffs  = np.append(cd, coeffs)
        widths  = np.append(len(cd), widths)
        if level==levels-1:
            coeffs = np.append(ca, coeffs)
            widths = np.append(len(ca), widths)
        orig = ca

    return coeffs, widths, alerts


def idwt1(ca, cd, wavelet):
    
    _, _, lo, hi = mother(wavelet)

    navg  = int(int(len(lo))/2 + int(len(hi))/2)
    npts  = len(cd)*2
    ufact = 2           # up sample factor of 2 

    # Processing steps
    # - upsample by factor of 2
    # - ensure even number of points
    # - pad with periodic data
    # - convolve with wavelet mother kernel
    # - repeat for both approx and detail coeffs
    
    ca = np.append(np.insert(ca, slice(1,None,ufact-1), 0.0), 0.0)  
    ca = np.append(ca, ca[-1]) if len(ca)%2 else ca 
    ca = np.pad(ca, (int(navg/2),int(navg/2)), 'wrap')
    recona = np.real(fftconvolve(ca, lo))

    cd = np.append(np.insert(cd, slice(1,None,ufact-1), 0.0), 0.0)  
    cd = np.append(cd, cd[-1]) if len(cd)%2 else cd 
    cd = np.pad(cd, (int(navg/2),int(navg/2)), 'wrap')
    recond = np.real(fftconvolve(cd, hi))
    
    recon = recona[navg-1:npts+navg-1] + recond[navg-1:npts+navg-1]
    
    return recon



def idwt(coeffs, wavelet, widths, alerts):

    levels = int(alerts[1])
    nca    = int(widths[0])
    ncd    = int(widths[1])
    ca     = coeffs[0:nca]
    cd     = coeffs[nca:2*nca]

    for i in range(levels):
        
        recon = idwt1(ca,cd,wavelet)
            
        nca += ncd
        if i < levels-1:
            ca  = recon
            ncd = widths[i+2]
            cd  = coeffs[nca:nca+ncd]

            if len(ca) > len(cd):
                t = len(ca)-len(cd)
                lent = int(np.floor(t * 0.5))
                ca = ca[:lent+len(cd)]
                ca = ca[lent:]
    
    pad   = int(alerts[0])
    recon = recon[0:len(recon)-pad]
    
    return recon


# -----------------------------------------------------------------------------


def _test_equivalency():
    '''
    Are coefficients the same for wavepy and pywavelets library calls?
    
    '''
    import pywt
    import wavepy as wv
    
    data = data64

    wavelet = 'coif3'   
    _mode = 'per'
    base_level = int(np.log(len(data))/np.log(2))   
    
    coeffs0 = pywt.wavedec(data, wavelet, _mode, level=base_level)
    [coeffs1,length1,flag1] = wv.dwt.dwt(data, base_level, wavelet, _mode)
    coeffs2,length2,flag2 = dwt(data, base_level, wavelet)
    diffA = np.concatenate(coeffs0) - coeffs1
    diffB = coeffs1 - coeffs2
    
    # first 4 coeffs for pywavelet are different from other libs, but we never
    # zero these out since they are the broadest dyads, so it is a moot point.
    print "max diffA = " + str(np.max(diffA[5:]))
    print "max diffB = " + str(np.max(diffB))

    recon0 = pywt.waverec(coeffs0, wavelet, _mode)
    recon1 = wv.dwt.idwt(coeffs1, wavelet, length1, flag1)
    recon2 = idwt(coeffs2, wavelet, length2, flag2)
    diffC = recon0 - recon1
    diffD = recon1 - recon2
    
    print "max diffC = " + str(np.max(diffC))
    print "max diffD = " + str(np.max(diffD))
    

data64 = [   3.75646062e-01,  -7.52931591e-01,  -9.85668931e-01,
            -5.71847181e-01,  -4.12297490e-01,   5.94913227e-01,
            -7.60136820e-01,  -8.21366067e-01,   4.73895513e-02,
             7.18766056e-01,   5.64785518e-01,  -5.76128617e-01,
            -6.65498320e-01,   4.35884338e-01,  -8.77145793e-01,
            -2.30297001e-01,  -7.76746230e-01,  -3.13412228e-01,
             6.87443670e-01,   1.14553782e-01,   5.66057710e-01,
            -8.77337090e-01,  -6.39754937e-01,   7.18250389e-01,
            -9.24781352e-01,   9.88529513e-01,   5.45465600e-02,
            -8.35248333e-01,  -4.40469828e-01,   1.46422657e-01,
            -1.29651675e-01,  -2.50870615e-01,  -3.52361713e-01,
            -3.62400134e-01,   3.34141270e-01,  -8.83583193e-01,
            -9.70013743e-02,  -7.45088469e-01,  -2.96155143e-01,
             1.61548515e-01,   4.04399869e-01,   4.75285614e-01,
            -3.78595158e-01,   5.19088161e-01,  -1.16044345e-01,
            -7.51618934e-01,  -5.45780616e-01,   9.18209827e-01,
            -6.53026178e-01,   2.39033374e-01,  -6.95793553e-01,
             3.08469171e-01,   7.76517411e-01,   7.80547551e-01,
            -8.68320975e-01,  -8.94686333e-02,   1.14572022e-01,
             6.44247703e-01,   4.11723423e-01,  -8.62504626e-01,
            -6.17812166e-01,   5.91205829e-01,  -9.95255684e-01,
            -7.37408598e-01 ]


if __name__ == '__main__':
    _test_equivalency()

#     import cProfile
#     cProfile.run('_test_timing()')
     

        


