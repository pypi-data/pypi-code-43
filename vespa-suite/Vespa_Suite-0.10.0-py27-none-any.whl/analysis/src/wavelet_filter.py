# Python modules
from __future__ import division

# 3rd party modules
import numpy as np
import copy

# Our modules
import vespa.common.wavelet_1d as vw1d

try:
    import pywt
    flag1 = 'pywavelets'
except:
    flag1 = 'local'


def wavelet_filter_pywt_original(data, thresh, scale, dyadmin):
    '''
    =========
    Arguments 
    =========
    **data:**  [array][float]

      dependent data to be filtered

    **thresh:**  [float]

      value in points for the minimum scale wavelet to be left in the result
      based on the linewidth value passed in from the application

    **scale:**  [float]

      multiplier of thresh, to make result have even broader terms

    **dyadmin:**  [float]

      hard value of the smallest scale object allowed regardless of thresh
      and scale values.


    =========== 
    Description
    ===========   
    The wavelet filter uses the library PyWavelets (pywt).
    
    From the website (http://www.pybytes.com/pywavelets/):
    PyWavelets is a free Open Source wavelet transform software for Python 
    programming language. It is written in Python, Pyrex/Cython and C for 
    a mix of easy and powerful high-level interface and the best performance.
    
    The implementation below is meant to be used as a method for estimating the
    signals that compose a baseline with broad signals that change slowly. It is
    performed by using the discrete wavelet transform (DWT) on the data to be 
    estimated. Then, some of the smaller scale dyad coefficients are set to zero, 
    and the inverse DWT is performed. 
    
    Algorithm
    ---------
    We use wavedec because it returns a list of arrays that correspond to
    dyad coeffs. So to get rid of a whole dyad of coeffs, we just have to 
    multiply the numpy array by zero. That is, gtting rid of one of the 
    arrays in the coeffs list is the same as zeroing a whole 2^N category. 
    
    To have some room to filter at different levels of broadness, I found 
    that the pywt.dwt_max_level() method did not typically set the level to
    a very big dyad range since it returns a "useful" level of decomposition
    not the complete decomposition. Empirically, I found that for arrays of
    32 - 2048 points, if I leave 8 coeffs in the approximation coeffs array, 
    and 8 more in the first details coefs array, then I have a workable 
    number of decimation levels to work with. 
    
    Thus the base_level calc below with the magic number 32. For 128 points,
    128 / 32 = 4 which gives us dyad arrays of 8, 16, 32, 64 to work with.
    and this scales to bigger data arrays too, with 128, 256 etc dyad levels.
    
    We use line width as a criterion for removing wavelet coefficients
    that have features on smaller scales. This results in a filtered signal
    that with broad components that change broadly. 
    
    Here we calculate which of two values will determine the broadness of 
    the reconstructed signal, 1) peak LW times a scaling multiplier, or 
    2) a hard minimum scale value. We calc each and use the bigger one.

    ======    
    Syntax
    ====== 
    ::

      res = wavelet_filter_pywt_original(data, thresh, scale, dyadmin)

    ''' 
    npts   = np.size(data)
    
    # Use the Coiflet 3 wavelet (18 data points), for historical reasons 
    wavelet = pywt.Wavelet('coif3')   
    
    # per - periodization - is like periodic-padding but gives the smallest 
    #       possible number of decomposition coefficients. Wavedec and waverec 
    #       methods must be performed with the same mode.
    _mode = 'per'

    # hard set level value empirically - see note above
    max_level  = int(np.log(len(data))/np.log(2))    
    base_level = int(len(data) / 32) 
    base_level = base_level if base_level < max_level else max_level
    
    coeffs  = pywt.wavedec(data, wavelet, _mode, level=base_level)

    # Calculate criterion for removing wavelet coefficients with features on 
    # smaller scales using either line width or a hard minimum scale value. 
    scale_mult = 1 if scale < 1 else scale
    lw_thresh  = np.where(thresh >  1, thresh, 1)  # this is in points
    lw_thresh *= scale_mult
    hard_min   = np.where(dyadmin > 1, dyadmin, 1) 
    width = np.where(hard_min > lw_thresh, hard_min, lw_thresh)
    
    # now we need to apply the calculated filtering width to the coeffs
    # and decide which ones to use in the reconstruction.
    filtered_coeffs = [coeffs[0]]
    for coeff in coeffs[1:]:
        width_of_each_dyad = npts/len(coeff)
        if width_of_each_dyad > width:
            filtered_coeffs.append(coeff.copy())
        else:
            filtered_coeffs.append(coeff.copy()*0)
    
    res = pywt.waverec(filtered_coeffs, wavelet, _mode)

    return res, coeffs, filtered_coeffs, base_level



def wavelet_filter_pywt_new(data, thresh, scale, dyadmin):
    '''
    =========
    Arguments 
    =========
    **data:**  [array][float]

      dependent data to be filtered

    **thresh:**  [float]

      value in points for the minimum scale wavelet to be left in the result
      based on the linewidth value passed in from the application

    **scale:**  [float]

      multiplier of thresh, to make result have even broader terms

    **dyadmin:**  [float]

      hard value of the smallest scale object allowed regardless of thresh
      and scale values.

    ======    
    Syntax
    ====== 
    ::

      res = wavelet_filter_pywt_new(data, thresh, scale, dyadmin)

    ''' 
    # Use the Coiflet 3 wavelet (18 data points), for historical reasons 
    wavelet = 'coif3' 
    wavelet = pywt.Wavelet('coif3')
    _mode   = 'per'

    # hard set level value empirically - see note above    
    base_level = int((np.log(len(data)) / np.log(2)) ) 
    
    coeffs2 = pywt.wavedec(data, wavelet, _mode, base_level)

    coeffs = np.concatenate(coeffs2)
    

    # Calculate criterion for removing wavelet coefficients with features on 
    # smaller scales using either line width or a hard minimum scale value. 
    scale_mult = 1 if scale  < 1 else scale   # float, multiplier
    lw_thresh  = 1 if thresh < 1 else thresh  # in points
    lw_thresh *= scale_mult
    
    hard_thresh = 2 if dyadmin < 2 else dyadmin  # in points
    
    width = hard_thresh if hard_thresh > lw_thresh else lw_thresh
    width = np.floor(np.log(width)/np.log(2))
    
    # Convert base2 dyad widths into index into the DWT result
    # - if width=1, then index==base_level, which would zero out all coeffs
    #   in the DWT results
    # - added (-1) to this line to always leave at least 2 coeffs to be 
    #   transformed back
    # - empirically, this also keeps result a bit smoother, too
    
    indx = base_level - width  
    indx = int(2**indx) 
    
    # now we need to apply the calculated filtering width to the coeffs
    # and decide which ones to use in the reconstruction.
    filtered_coeffs = coeffs.copy()
    filtered_coeffs[indx:] = 0.0 
    
    # restack flattened coeffs so we can apply waverec() 
    tmp = [np.array(filtered_coeffs[0:1]),]
    for i in range(0,base_level):
        tmp.append(np.array(filtered_coeffs[2**(i):2**(i+1)]))
        
    res = pywt.waverec(tmp, wavelet, _mode)

    return res, coeffs, filtered_coeffs, base_level


def wavelet_filter_local(data, thresh, scale, dyadmin):
    '''
    =========
    Arguments 
    =========
    **data:**    [array][float]  dependent data to be filtered

    **thresh:**  [float]  value in points for the minimum scale wavelet to be 
                 left in the result based on the linewidth value passed in from 
                 the application

    **scale:**   [float] multiplier of thresh, to make result have even broader terms

    **dyadmin:**  [float] hard value of the smallest scale object allowed regardless 
                  of thresh and scale values.

    =========== 
    Description
    ===========   
    The wavelet filter uses our native wavelets methods.


    ======    
    Syntax
    ====== 
    ::

      res = wavelet_filter_local(data, thresh, scale, dyadmin)

    ''' 
    # Use the Coiflet 3 wavelet (18 data points), for historical reasons 
    wavelet = 'coif3' 

    # hard set level value empirically - see note above    
    base_level = int((np.log(len(data)) / np.log(2)) ) 
    
    coeffs, widths, alerts = vw1d.dwt(data, base_level, wavelet)

    # Calculate criterion for removing wavelet coefficients with features on 
    # smaller scales using either line width or a hard minimum scale value. 
    scale_mult = 1 if scale  < 1 else scale   # float, multiplier
    lw_thresh  = 1 if thresh < 1 else thresh  # in points
    lw_thresh *= scale_mult
    
    hard_thresh = 2 if dyadmin < 2 else dyadmin  # in points
    
    width = hard_thresh if hard_thresh > lw_thresh else lw_thresh
    width = np.floor(np.log(width)/np.log(2))
    
    # Convert base2 dyad widths into index into the DWT result
    # - if width=1, then index==base_level, which would zero out all coeffs
    #   in the DWT results
    # - user needs to ensure that this does not happen
    # - if we subtract 1 from indx to prevent this from happening we are no
    #   longer working quite the same way as wavepy dwt/idwt calls
    
    indx = base_level - width  
    indx = 2**indx
    
    # now we need to apply the calculated filtering width to the coeffs
    # and decide which ones to use in the reconstruction.
    filtered_coeffs = coeffs.copy()
    filtered_coeffs[indx:] = 0.0 
    
    res = vw1d.idwt(filtered_coeffs, wavelet, widths, alerts)       

    return res, coeffs, filtered_coeffs, base_level


def wavelet_filter(data, thresh, scale, dyadmin):
    # the extra return values below are good for error checking 
    # in the test code below. Here we just return result

    if flag1 == 'local':
        result, coefs, filts, levels = wavelet_filter_local(data, thresh, scale, dyadmin)

    else:
        result, coefs, filts, levels = wavelet_filter_pywt_new(data, thresh, scale, dyadmin)
        #result, coefs, filts, levels = wavelet_filter_pywt_original(data, thresh, scale, dyadmin)

    return result
    

#------------------------------------------------------------------------------
# Test Code 
    
def _test():

    import pylab

    thresh  = 1      # should be in points
    scale   = 1      # multiplier for thresh
    dyadmin = 8     # in points
    
    result1, coef1, filt1, base_level1 = wavelet_filter_pywt_original( data64, thresh, scale, dyadmin)
    result2, coef2, filt2, base_level2 = wavelet_filter_pywt_new(data64, thresh, scale, dyadmin)
    result3, coef3, filt3, base_level3 = wavelet_filter_local(data64, thresh, scale, dyadmin)

    diff12 = result1 - result2
    diff13 = result1 - result3 
    diff23 = result2 - result3
    
    print "max diff12 = " + str(np.max(diff12))
    print "max diff13 = " + str(np.max(diff13))
    print "max diff23 = " + str(np.max(diff23))

    pylab.plot(data64)
    pylab.plot(result1, 'b', linewidth=2)
    pylab.plot(result2, 'r', linewidth=2)
    pylab.plot(result3, 'g', linewidth=2)
    pylab.show()
    
    bob = 10


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

data512 = [  3.75646062e-01,  -7.52931591e-01,  -9.85668931e-01,
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
            -7.37408598e-01,   1.52337717e-01,   4.60020922e-01,
             8.21901456e-01,  -9.66741616e-01,  -7.13453211e-01,
             8.69856629e-01,   4.31479220e-01,   2.34180480e-01,
            -1.20795429e-01,  -7.58481778e-01,   8.90794489e-02,
            -5.88339228e-01,  -7.45162552e-01,  -1.18647667e-01,
             6.39840811e-01,   7.06636122e-01,  -4.35238552e-01,
             6.05690924e-02,  -4.28108549e-02,   8.28852045e-01,
            -3.44695249e-01,   8.80718161e-01,  -8.27529814e-02,
             8.43118182e-01,   1.08104486e-01,  -1.21476635e-01,
             3.44499847e-01,  -1.53870048e-01,   6.88370266e-01,
             2.00700418e-01,  -1.38963979e-01,   1.46076051e-01,
            -4.43601013e-01,   3.73229911e-01,  -4.12963533e-01,
            -5.61652322e-01,   7.16634494e-01,  -2.16206010e-01,
            -5.47902132e-01,   2.97978476e-01,  -2.40810421e-01,
            -1.38477923e-01,  -1.96537509e-01,   8.41600378e-01,
            -7.01048991e-01,  -3.26011343e-01,   7.40944020e-01,
             7.92013355e-01,   9.58039686e-01,  -8.66003316e-02,
            -7.47484615e-01,  -1.03203783e-01,   3.90961877e-01,
             5.88645448e-02,   4.84981482e-01,   2.14750636e-01,
            -9.16891573e-01,  -8.77766272e-01,  -1.22928034e-01,
             4.39233853e-01,   9.64885343e-01,   2.38159680e-01,
            -8.24668621e-01,   8.78599180e-01,  -9.71170460e-01,
             9.58521116e-01,   7.51664111e-01,   5.83129360e-01,
             8.18686558e-01,  -1.90503960e-01,   4.82251426e-01,
             7.79003931e-02,   7.96218007e-01,   9.04136551e-02,
             9.38782651e-01,   3.22636088e-01,   6.63347618e-01,
            -2.08240173e-02,   7.61368827e-01,   2.42745073e-01,
             3.36966919e-01,   9.65048456e-01,   7.47751586e-01,
            -1.31341183e-01,  -4.14529822e-01,   4.81193887e-01,
            -1.57069023e-01,  -4.98932912e-01,  -5.02207453e-01,
             8.97461376e-01,   5.68539054e-01,  -3.33004156e-02,
             6.40258634e-01,  -1.08483820e-01,  -3.63935223e-01,
            -3.58784069e-01,  -8.57522821e-01,   6.52347850e-01,
             8.88866217e-01,   9.27036598e-02,  -9.17952594e-01,
             4.88133887e-01,  -8.99923262e-01,  -1.24754874e-01,
            -9.83981267e-01,   6.71859583e-01,   2.22285782e-01,
             9.99491884e-01,  -2.13793391e-01,   5.41308881e-01,
            -2.48864956e-01,  -6.41215565e-01,   2.08976294e-01,
            -5.01981400e-01,   8.67521010e-01,   4.53691038e-01,
             6.60846497e-01,   6.92642013e-01,  -9.26516590e-01,
            -5.66417221e-01,   6.82901169e-01,   1.76197692e-01,
            -6.29402014e-01,   6.23453301e-01,  -9.95167316e-01,
             7.94616074e-01,   1.44023802e-01,  -6.21099327e-01,
             5.38968798e-01,   4.72721623e-02,  -7.54607060e-01,
             9.40424132e-01,   5.25312554e-01,  -5.48266309e-01,
             1.30897816e-01,  -9.09033292e-01,   8.22968694e-01,
             2.33117823e-01,  -8.17960406e-02,  -8.64572788e-01,
             7.79842416e-01,  -6.94409173e-01,  -3.49348906e-01,
             3.60627293e-01,  -8.94592720e-01,  -5.23203585e-01,
             5.10816769e-01,   7.92351016e-01,   3.44594756e-01,
            -7.41861216e-01,  -1.46910781e-01,   9.82974741e-01,
             2.84467001e-02,   1.64031277e-01,   8.37959712e-01,
            -8.40666266e-01,  -6.77120307e-01,   2.99774608e-01,
             3.62513103e-01,   5.38258600e-01,   8.87428596e-01,
             7.37883213e-01,  -6.12987965e-01,   9.52064912e-01,
            -8.01530718e-01,  -6.25001860e-01,   1.38489453e-04,
             1.02482091e-01,  -5.19325116e-01,   3.09194213e-02,
            -6.69567820e-01,  -3.15423254e-01,  -7.08278016e-03,
            -9.05573565e-01,   7.83573223e-01,  -3.08813628e-01,
            -6.48352781e-02,   6.87948597e-01,  -8.13890542e-01,
             8.77276600e-01,  -8.58673551e-01,   8.47352080e-01,
             6.75431125e-01,   2.46511055e-01,  -7.05090619e-01,
             3.72889943e-01,  -4.05336117e-01,   4.99878296e-01,
            -7.54398410e-01,   4.76555557e-01,   8.53587880e-01,
            -6.74342664e-01,   1.43771273e-01,  -2.78449879e-01,
            -8.67673827e-01,   7.22242336e-01,  -7.56848307e-01,
            -4.36321061e-01,  -7.11850991e-01,   7.81862734e-01,
             5.74320667e-02,  -6.43750668e-01,   3.93838266e-01,
            -5.04486281e-01,  -3.76942251e-01,   2.43921479e-01,
             6.22354458e-01,   8.11172039e-01,  -2.91633509e-01,
             6.77349438e-01,   1.97141889e-02,   7.47133950e-01,
             9.37125977e-01,   6.67374688e-01,  -3.64348368e-01,
             4.25802283e-02,  -9.47268046e-01,   6.27707597e-01,
            -8.90162011e-03,  -1.36392965e-01,  -5.63029045e-01,
            -3.89262852e-01,   7.08105979e-01,   9.53310308e-01,
            -2.47867490e-01,   1.95516715e-01,   1.13597696e-01,
             5.36048253e-01,   7.18607062e-01,  -2.45340991e-01,
            -3.38850890e-01,   4.00847670e-01,   1.26748532e-01,
             4.58776106e-01,   9.93179657e-01,  -1.98153124e-01,
            -3.85050156e-02,   4.56963126e-01,   9.02595155e-01,
            -6.07300791e-01,   1.23671886e-01,  -6.71789927e-01,
            -8.86058382e-01,  -6.48187379e-01,  -8.70622860e-01,
            -1.03694821e-01,  -2.19446936e-01,   9.60393902e-01,
            -3.90512796e-01,  -3.11004284e-01,   5.70514010e-01,
            -2.62504010e-01,   2.81325934e-01,  -5.84846389e-01,
             5.52392972e-01,  -9.23787477e-01,   1.46984533e-01,
            -4.32873210e-01,  -4.46254902e-01,   5.88835905e-01,
            -5.40821116e-01,   5.68364794e-01,   5.84685596e-01,
             1.02966387e-01,   7.67745330e-01,   8.79335041e-01,
            -9.83259946e-01,  -6.07942129e-02,  -8.91894295e-01,
             9.06429133e-01,   4.80018558e-01,  -5.29011841e-01,
            -3.30991724e-01,   8.84853932e-01,   4.63172732e-01,
            -8.13350125e-02,  -3.35379843e-01,  -4.21569785e-01,
             9.14902200e-01,  -1.02960841e-01,   4.78850954e-01,
             2.81068398e-01,   3.71847096e-01,   6.87768377e-01,
            -1.90317541e-01,  -1.36280752e-01,   5.66978735e-01,
            -9.95156265e-01,  -6.72689294e-01,  -7.47492937e-01,
             7.38557742e-01,  -8.65115459e-02,  -7.23979408e-01,
            -6.36044260e-01,  -7.52825198e-02,  -4.74794016e-01,
            -4.77892883e-01,   9.28941787e-01,   1.81191617e-01,
            -2.65661249e-01,   9.22730971e-01,   1.25716576e-01,
             7.86155538e-01,   5.76023433e-01,  -8.71700165e-01,
            -7.02002362e-01,  -1.18808819e-01,  -3.59081475e-01,
             8.20239807e-01,  -8.60990964e-01,   1.05585956e-02,
             3.50620919e-01,   5.78417011e-01,   2.97633660e-01,
            -1.81421820e-01,   1.13116675e-01,  -9.57084082e-01,
             9.10525895e-01,  -1.97179881e-01,  -4.18923803e-01,
             7.30963793e-01,   6.44411938e-01,   4.84521317e-01,
            -9.79993537e-01,  -1.90330187e-01,  -8.01735324e-01,
            -7.95116643e-01,   1.54861536e-02,   3.30498663e-01,
            -6.63741431e-01,  -3.22912197e-01,   9.08154143e-02,
            -4.86429206e-01,  -9.65868088e-01,  -5.00716650e-01,
            -5.14083836e-02,  -7.06573893e-01,   2.41422991e-01,
            -7.03571811e-01,   5.47600737e-01,  -3.99917562e-02,
             8.53509139e-01,   1.87509196e-01,   7.28863989e-01,
             2.88058869e-01,  -9.55473817e-01,   3.96652473e-01,
            -2.39105589e-02,  -4.74398641e-01,   6.71702424e-01,
            -1.61986495e-02,   9.52447097e-01,   4.82877272e-01,
            -5.08641616e-01,   3.45319487e-01,   2.71040683e-01,
            -3.74967398e-01,   4.80706559e-01,  -2.76228679e-02,
             7.86477643e-01,   8.79749218e-01,  -5.12384365e-02,
             7.67550559e-01,   7.21522412e-02,   2.89846119e-01,
             6.58384232e-01,   5.26406546e-01,   4.28591136e-01,
            -3.03239658e-01,   3.20518747e-01,  -3.61642452e-01,
            -2.57154869e-01,  -8.59475882e-01,  -2.96075091e-01,
             7.15430907e-01,   8.72760079e-01,   5.36587145e-01,
             9.49043455e-02,  -6.40281593e-01,   6.09692168e-01,
            -3.08764967e-01,  -1.25483568e-01,   1.81656523e-01,
            -9.90980282e-01,   1.78073398e-01,  -6.96875650e-02,
            -8.06939906e-02,   5.93343399e-01,   9.70264981e-01,
             8.24597775e-01,  -2.51284816e-01,  -4.48625709e-01,
            -4.24003224e-01,   5.15295534e-01,  -7.24597146e-01,
             8.92237969e-01,   9.82823322e-01,   2.69250630e-01,
             2.48893842e-01,   7.66001362e-01,  -7.70151578e-01,
             1.61326410e-01,  -5.74888290e-01,   3.65707714e-02,
             4.39364502e-01,  -9.82345243e-01,  -3.21377511e-01,
             2.33164113e-01,  -2.54690453e-01,   2.99896308e-01,
            -6.48028298e-01,   4.46728061e-01,   8.02453136e-01,
            -6.80686776e-01,   4.46120216e-01,  -2.61524181e-01,
             7.05794583e-01,   9.58443474e-02,  -6.22550571e-01,
             1.74824534e-01,  -8.19901157e-01,  -4.69628531e-01,
            -5.99217191e-01,   9.18984389e-01,   1.58504489e-01,
            -2.53801460e-01,  -1.93454952e-01,  -5.79757511e-01,
             6.13962908e-01,   8.06061643e-03,  -1.84706278e-01,
            -7.82907430e-01,  -5.00813255e-01,   4.50640774e-01,
            -1.43900252e-01,  -8.97313703e-01,   2.34970202e-02,
             8.35375101e-01,  -5.17714066e-01,  -8.25744032e-02,
             8.31770770e-01,   8.58964103e-01,  -5.68023003e-01,
            -6.61441935e-01,  -7.33147669e-01,   5.53626373e-01,
             7.01150037e-01,   7.10635970e-01]


if __name__ == '__main__':
    
    _test()
    
#    import cProfile
#    cProfile.run('_test2()')
 