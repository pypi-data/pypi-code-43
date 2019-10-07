# Python modules
from __future__ import division
import math

# 3rd party modules
import numpy as np

# Our modules
import vespa.common.util.ppm as util_ppm
import vespa.common.util.math_ as util_math


# This is a constant for Gaussian apodization.
# FIXME - 0.6 is a magic number. Please document.
_GAUSSIAN_APODIZATION_K = math.pi * 0.6

# This is an anonymous object to which I can attach some attributes. I pass
# instances to a few functions that require objects.
class _DatasetWithNewZerofill(object):

    def __init__(self, dataset, zf_factor=1):

        self.spectral_dims    = list(dataset.spectral_dims)
        self.zfmult           = dataset.zero_fill_multiplier * zf_factor
        self.spectral_dims[0] = round(self.spectral_dims[0] * zf_factor)
        self.spectral_hpp     = dataset.sw / self.spectral_dims[0]
        self.midppm           = dataset.midppm
        self.resppm           = dataset.resppm
        self.frequency        = dataset.frequency



def apodize(data, width, type_):
    """
    Given data to apodize, width, and apodization type, returns the line
    shape.

    data in this instance is the digitization time course for the spectral data
    to be apodized, namely: 0, 1*dwelltime, 2*dwelltime, ...

    The type can be 'G' for Gaussian apodization or 'L' for Lorentzian.

    Only the first letter of the type is considered and it is case insensitive,
    so 'G', 'g', 'gaussian', 'GAUSSIAN', 'Geronimo', 'glop', 'GGG', etc. all
    imply Gaussian.
    """
    if type_:
        # Grab the first letter and uppercase it.
        type_ = type_.upper()[0]

    if type_ == 'G':
        # Gaussian
        lineshape = -(width * _GAUSSIAN_APODIZATION_K * data) ** 2
        lineshape = util_math.safe_exp(lineshape, 0)
    elif type_ == 'L':
        # Lorentzian
        lineshape = -(width * math.pi * data)
        lineshape = util_math.safe_exp(lineshape, 0)
    else:
        raise ValueError, """Bad apodization type "{0}" """.format(type_)

    return lineshape


def calculate_fid(areas, ppms, phases, dataset, calc_peakppm=True):
    """
    =========
    Arguments
    =========
    **areas:**  [list][float]

      amplitudes for each spectral line

    **ppms:**  [list][float]

      ppm values for each spectral line

    **phases:**  [list][float]

      ppm values for each spectral line

    **dataset:**  [object][Dataset]

      container providing resolution for generic spectrum

    **calc_peakppm:** [keyword][bool][default=True]

      flag to determine if ppm value for max peak is calculated.

    ===========
    Description
    ===========
    Sums all the ASCII lines for a single generic "metabolite"
    into a complex FID at the resolution of the current dataset.
    There is no line broadening applied by this method

    ======
    Syntax
    ======
    ::

      fid = calculate_fid( areas, ppms, phases, dataset, nopeakppm=True )

    """
    acqdim0 = dataset.raw_dims[0]
    td      = 1.0/dataset.sw
    arr1    = np.zeros(acqdim0,float) + 1.0
    freqs   = util_ppm.ppm2hz(np.array(ppms), dataset) * 2.0 * np.pi
    phases  = np.array(phases) * np.pi / 180.0
    npk     = np.size(freqs)

    xx = (np.arange(npk*acqdim0, dtype='float') % acqdim0) * td
    xx.shape = npk,acqdim0

    am  = np.outer(np.array(areas),arr1)
    fr  = np.outer(freqs,arr1)
    ph  = np.outer(phases,arr1)

    tmp = am * np.exp(1j * fr * xx) * np.exp(1j * ph)
    tmp = np.sum(tmp, axis=0)

    if calc_peakppm:
        # Determine PPM of max amplitude of this metabolite ---
        hires_dataset = _DatasetWithNewZerofill(dataset, 4.0)
    
        dim0    = int(round(acqdim0 * dataset.zero_fill_multiplier * 4.0))
        acqsw   = dataset.sw

        xx  = np.arange(acqdim0)/acqsw
        dat = np.zeros(dim0, complex)

        lshape = apodize(xx, 2.0, 'Gaussian') # 1Hz Gaussian Lineshape

        dat[0:acqdim0] = tmp * lshape

        dat  = np.fft.fft(dat) / len(dat)
        r    = max(dat.real)
        indx = np.where(r == dat.real)[0][0]

        pkppm = util_ppm.pts2ppm(indx, hires_dataset)

        return tmp, pkppm

    return tmp, None




def calculate_spectrum(areas, ppms, phases, dataset, ta=0.07, tb=0.07):
    """
    =========
    Arguments
    =========
    **areas:**  [list][float]

      xxxx

    **ppms:**  [list][float]

      xxxx

    **phases:**  [list][float]

      xxxx

    **dataset:**  [object]

      container with resolution of spectrum to be created

    **ta:**  [keyword][float][default=0.07]

      xxxx

    **tb:**  [keyword][float][default=0.07]

      should be array of text strings in db format.  If
      set, then is used instead of dbfilename to fill db


    ===========
    Description
    ===========
    xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx xxx
    xxx xxx xxx xxx xxx xxx

    ======
    Syntax
    ======
    ::

      spectrum = calculate_spectrum(areas, ppms, phases, dataset, ta=0.07, tb=0.07)

    """
    basis, pkppm = calculate_fid(areas, ppms, phases, dataset, calc_peakppm=False)

    zfmult   = dataset.zero_fill_multiplier
    acqdim0  = dataset.raw_dims[0]

    # create lineshape
    td    = 1.0/dataset.sw
    off   = round(1.0 * acqdim0 * dataset.echopeak/100.0) * td
    xx    = np.arange(acqdim0) * td
    xxx   = abs(xx-off)
    decay = xx/ta + (xxx/tb)**2
    indx  = np.where(decay > 50)
    cnt   = np.size(indx)
    if cnt > 0:
        decay[indx] = 50
    lshape  = np.exp(-decay)
    
    # create spectrum by applying lineshape and doing iFFT and lineshape 
    tmp = np.zeros(int(round(acqdim0 * zfmult)), complex)
    tmp[0:acqdim0] = basis * lshape
    tmp[0] *= 0.5

    final_spectrum = np.fft.fft(tmp) / len(tmp)

    return final_spectrum


def chop(data):
    """
    Alternates points between positive and negative
    That is, even points are multiplied by 1
    and odd points are multiplied by -1
    """
    return data * ((((np.arange(len(data)) + 1) % 2) * 2) - 1)


def clip(value, minimum, maximum=None):
    """ Returns value such that minimum <= value <= maximum """
    if value < minimum:
        value = minimum
    if (maximum is not None) and (value > maximum):
        value = maximum

    return value


def full_width_half_max(data, minfloor=False, positive=False):
    """
    Finds maximum in data then searches left and right to find
    the point at half the amplitude of the max point.  Adds
    indices together to get a Full Width Half Max value.
    """

    if positive:
        data = np.abs(data)
    else:
        data = data.copy()

    if minfloor:
        floor = np.min(data)
        floor = floor if floor>0 else 0
    else:
        floor = 0.0


    data = data.real
    peak = np.max(data)
    peak_index = np.argmax(data)
    half_peak = peak - ((peak-floor)/2.0)

    # Find the half max to the right of the peak
    right_index = peak_index
    while (data[right_index] >= half_peak) and (right_index < len(data) - 1):
        right_index += 1

    # Find the half max to the left of the peak
    left_index = peak_index
    while (data[left_index] >= half_peak) and left_index:
        left_index -= 1

    return right_index - left_index


def get_exponential_filter(length, center, line_broaden, sweep_width):
    # Get exponential function
    echo_at = round(length*center)
    echo_at = np.where(echo_at > 0, echo_at, 0)

    if sweep_width == 0:
        damper = line_broaden / (length - echo_at)
    else:
        damper = np.pi * line_broaden / sweep_width

    index = abs(np.arange(length) - echo_at)
    expo = index * damper

    return  util_math.safe_exp(-expo)


def get_gaussian_filter(length, center, line_broaden, sweep_width):
    # Get Gaussian function
    echo_at = round(length*center)
    echo_at = np.where(echo_at > 0, echo_at, 0)

    if sweep_width == 0:
        npts = float(length - echo_at)
        damper = line_broaden / npts**2.
    else:
        damper = (0.6 * np.pi * line_broaden / sweep_width)**2

    tindex = abs(np.arange(length) - echo_at)
    expo = tindex**2 * damper

    return util_math.safe_exp(-expo)


def hamming2(N, echo_position):
    # To obtain Hamming function with value=1.0 at point=N/2+1
    n1 = int(N * echo_position)
    n1 = np.where(n1 > 0, n1, 0)
    n2 = N - n1

    if n1 == 0:
        filter_length = 2*n2-1
        ret2 = np.hamming(filter_length + 1)[0:filter_length]    # right half
        return ret2[N-1:2*N-1]
    elif n1 == N:
        filter_length = 2*n1-1
        ret1 = np.hamming(filter_length + 1)[0:filter_length]    # left half
        return ret1[0:n1-1]
    else:
        filter_length = 2*n1+1
        ret1 = np.hamming(filter_length + 1)[0:filter_length]    # left half
        filter_length = 2*n2+1
        ret2 = np.hamming(filter_length + 1)[0:filter_length]    # right half
        return [ret1[0:n1],ret2[n2+1:2*n2-1]]


def voigt_width( ta, tb, dataset, hzres=0.1 ):

    if hzres < 0.01:
        hzres = 0.1

    zfmult = dataset.zero_fill_multiplier

    # Calc zerofill needed for < hzres Hz per point
    hpp  = dataset.raw_hpp / zfmult
    mult = 1
    while hpp >= hzres:
       hpp  = hpp  / 2.0
       mult = mult * 2.0

    npts    = dataset.raw_dims[0]
    nptszf1 = npts * zfmult * mult
    nptszf2 = npts * zfmult
    f1      = np.zeros(int(nptszf1), complex)
    f2      = np.zeros(int(nptszf2), complex)

    td      = 1.0/dataset.sw
    off     = round(1.0 * npts * dataset.echopeak/100.0) * td
    t       = np.arange(npts) * td              # for T2, always decreases with time
    ta      = ta if ta > 0.005 else 0.005       # Ta > 0
    tb      = tb if tb > 0.005 else 0.005       # Tb > 0

    # setup Lineshape
    expo    = t/ta + (t/tb)**2
    lshape  = util_math.safe_exp(-expo)
    lshape  = lshape + (1j*lshape*0)

    f1[0:npts] = lshape
    f1[0] *= 0.5
    f1 = np.fft.fft(f1) / nptszf1
    f1 = np.roll(f1, int(nptszf1 / 2))

    f2[0:npts] = lshape
    f2[0] *= 0.5
    f2 = np.fft.fft(f2) / nptszf2

    widpts = full_width_half_max(f1.real)
    peak_width = widpts * dataset.sw / nptszf1

    peak_norm = np.max(f2.real)
    peak_norm = 1.0/peak_norm

    return peak_width, peak_norm
