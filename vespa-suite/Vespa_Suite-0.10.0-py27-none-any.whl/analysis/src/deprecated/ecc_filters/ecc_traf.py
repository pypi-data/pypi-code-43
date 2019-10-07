# Python imports
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party imports
import numpy as np

# Vespa imports
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.
import ecc_filters.ecc_filter as ecc_filter
import functors.functor as functor
import vespa.common.util.xml_ as util_xml
import vespa.common.util.misc as util_misc

from vespa.common.constants import Deflate


#----------------------------------------------------------
# Trafficante Eddy Current Correction

def _create_panel(parent, tab, attributes):
    # This import is inline so that wx doesn't get imported unless we
    # receive an explicit request for a GUI object.
    import panel_traf

    return panel_traf.PanelTraf(parent, tab, attributes)


class EccTraf(ecc_filter.EccFilter):
    
    XML_VERSION = "1.0.0"

    ID = "6dbba247-a388-477e-b8ab-75d4ca3615e8"

    DISPLAY_NAME = 'Traf'

    def __init__(self, attributes=None):
        ecc_filter.EccFilter.__init__(self, attributes)

        self.ecc_raw = None
        self.ecc_dataset = None

        # this id is only used to find the dataset in the top level list
        # after a viff file is opened
        self.ecc_dataset_id = None
        
        self.functor = _FunctEccTraf()

        self._panel = None
        
        self._gui_data = None

        if attributes is not None:
            self.inflate(attributes)


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("------------- EccTraf ------------")
        lines =  u'\n'.join(lines)

        return lines


    def get_associated_datasets(self, is_main_dataset=True):
        """
        Returns a list of datasets associated with this object
        
        The 'is_main_dataset' flag allows the method to know if it is the top
        level dataset gathering associated datasets, or some dataset that is
        only associated with the top dataset. This is used to stop circular
        logic conditions where one or more datasets refer to each other.

        """

        # We don't want datasets being stored in VIFF files to collide with ids
        # in memory now, should they be loaded right back in again. So, in the 
        # dataset.deflate() method, the dataset.id is changed, deflated and 
        # then restored. Here we just return the unaltered list of associated
        # datasets
        
        if self.ecc_dataset:
            return [self.ecc_dataset]
        else:
            return []

        
    def get_panel(self, parent, tab):
        """Returns the panel (GUI) associated with this filter"""
        # self._panel is only created as needed. 
        if not self._panel:
            self._panel = _create_panel(parent, tab, self._gui_data)
            
        return self._panel
        

    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # Get my base class to deflate itself
            e = ecc_filter.EccFilter.deflate(self, flavor)
            
            if self.ecc_dataset:
                # handle the things that are specific to this class.

                # In the next line, we *have* to save the uuid values from the 
                # actual object rather than from the attribute above, in  
                # order for the associated dataset uuid to reflect the new id
                # that is given in the top level dataset. Associated datasets are
                # given new temporary uuid values so that if the main dataset is 
                # saved and immediately loaded back in, we do not get collisions
                # between the newly opened datasets and already existing ones.

                util_xml.TextSubElement(e, "ecc_dataset_id", self.ecc_dataset.id)

            if self.ecc_raw is not None:
                e.append(util_xml.numpy_array_to_element(self.ecc_raw, 'ecc_raw'))

            return e

        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            # Get my base class to inflate itself
            e = ecc_filter.EccFilter.inflate(self, source)

            # handle the things that are specific to this class.
            for name in ('ecc_dataset_id',):
                tmp = source.findtext(name)
                if tmp: 
                    setattr(self, name, tmp)

            ecc_raw = source.find("ecc_raw")
            if ecc_raw is not None:
                self.ecc_raw = util_xml.element_to_numpy_array(ecc_raw)

        elif hasattr(source, "keys"):
            raise NotImplementedError



class _FunctEccTraf(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        self.ecc_dataset = None
        self.ecc_raw = None
        

    ##### Standard Methods and Properties #####################################

    
    def update(self, other):   
        if other.ecc_handler.active: 
            self.ecc_dataset = other.ecc_handler.active.ecc_dataset
            self.ecc_raw = other.ecc_handler.active.ecc_raw
 
            

    def algorithm(self, chain):
        
        if self.ecc_dataset: 

            voxel = chain.voxel

            # water reference FID
            ecc = self.ecc_raw[voxel[2],voxel[1],voxel[0],:]

            # metabolite FID
            met = chain.data

            # sweep width
            sw = chain.sw

            # Call _refdeca_gm wih water reference FID and sw
            # to get amplitude and phase corrections and estimated T2
            [ampcor,phasecor,t2e] = self._refdeca_gm(ecc,sw)

            # Call _refdecb_gm with metabolite FID and outputs
            # from _refdeca_gm to obtained final corrected 
            # metabolite FID - modifies metaboilte FID in place
            metf = self._refdecb_gm(met,ampcor,phasecor,t2e,sw)

            chain.data = metf


    ##### Internal helper functions ##################################


    def _savitzky_golay(self, y, window_size, order, deriv=0):
        """
        Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
        The Savitzky-Golay filter removes high frequency noise from data.
        It has the advantage of preserving the original shape and
        features of the signal better than other types of filtering
        approaches, such as moving averages techhniques.
        Parameters
    
        Obtained from: http://www.scipy.org/Cookbook/SavitzkyGolay
        ----------
        y : array_like, shape (N,)
            the values of the time history of the signal.
        window_size : int
            the length of the window. Must be an odd integer number.
        order : int
            the order of the polynomial used in the filtering.
            Must be less then `window_size` - 1.
        deriv: int
            the order of the derivative to compute (default = 0 means only smoothing)
        Returns
        -------
        ys : ndarray, shape (N)
            the smoothed signal (or it's n-th derivative).
        Notes
        -----
        The Savitzky-Golay is a type of low-pass filter, particularly
        suited for smoothing noisy data. The main idea behind this
        approach is to make for each point a least-square fit with a
        polynomial of high order over a odd-sized window centered at
        the point.
        Examples
        --------
        t = np.linspace(-4, 4, 500)
        y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
        ysg = savitzky_golay(y, window_size=31, order=4)
        import matplotlib.pyplot as plt
        plt.plot(t, y, label='Noisy signal')
        plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
        plt.plot(t, ysg, 'r', label='Filtered signal')
        plt.legend()
        plt.show()
        References
        ----------
        .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
           Data by Simplified Least Squares Procedures. Analytical
           Chemistry, 1964, 36 (8), pp 1627-1639.
        .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
           W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
           Cambridge University Press ISBN-13: 9780521880688
        """
        try:
            window_size = np.abs(np.int(window_size))
            order = np.abs(np.int(order))
        except ValueError, msg:
            raise ValueError("window_size and order have to be of type int")
        if window_size % 2 != 1 or window_size < 1:
            raise TypeError("window_size size must be a positive odd number")
        if window_size < order + 2:
            raise TypeError("window_size is too small for the polynomials order")
        order_range = range(order+1)
        half_window = (window_size -1) // 2
        # precompute coefficients
        b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
        m = np.linalg.pinv(b).A[deriv]
        # pad the signal at the extremes with
        # values taken from the signal itself
        firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
        lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        return np.convolve( m, y, mode='valid')
    
    
    def _traf_gm(self, siglen, t2e, sw):
        """
        _traf_gm(siglen,t2e,sw)
        
        This function returns the standard complex TRAF filter for a
        signal length and estimated T2 (T2*) (in points) input.
        
        Input:
           siglen - signal length
           t2e - T2 (T2*) estimate (in points, i.e. relative to siglen)
        Output:
           complex TRAF filter
        
        """
        eps   = np.sqrt(np.finfo(np.float).eps)
        dwell = 1.0/float(sw)
        tim = np.arange(siglen)*dwell
        traff = np.array(np.zeros(siglen),np.complex)
        
        mE = np.zeros(siglen)
        mF = np.zeros(siglen)
        
        for i,t in enumerate(tim):
            if abs(t/t2e) < 25:
                mE[i] = np.exp(-t/t2e)
            else:
                mE[i] = eps
    
        for i,t in enumerate(tim):
            if abs((tim[-1] - t)/t2e) < 25:
                mF[i] = np.exp(-(tim[-1] - t)/t2e)
            else:
                mF[i] = 0.0
        
        mEE = mE * mE
        mFF = mF * mF
        mEF = mE * mF
        denom = mEE + mFF
        traff.real = (mEE + mEF)/denom
        traff.imag = (mEE - mEF)/denom
        
        return traff
    
    
    def _refdeca_gm(self, dcy,sw):
    
        """
        _refdeca_gm(h2o_ref,sw)
        Provides amp and phase corrections from water only signal
        ASSUMES APODIZATION USED FIRST (data first point halved) *******
        Checks for excessive corrections 
        Assumes files already added (or a single file)containing only water
        Data is dcy; sw known in Hz
        Set any parameters (lwfact for narrower metab lines)
        
        Input:
           h2o_ref - a water reference FID
           sw - sweep width in Hz
        Output:
           [AmpCor,PhaseCor,T2E]
           Ampcor - amplitude correction to multiply metabolite FID by
           Phasecor - phase correction to use on metabolite FID (length
                      of FID)
           T2E - T@ estimated from water reference FID
        """
        lwfact   = 1.2
        aCorrMax = 2.0
        
        # Time points
        t = (1./sw) * np.arange(len(dcy))
        
        # Work with absolute mode to obtain T2 estimate
        # Fits to beginning and end of FID (absolute mode)
        # Restore first data point for data
        data = np.abs(dcy)
        data[0] = 2.0*data[0]
        
        # Filter FID to minimize noise
        data = self._savitzky_golay(self._savitzky_golay(data, 15, 3), 13, 3)
        
        # Set regions to fit (Skip first 10 pts)
        mMax1 = data[10]
        mMin1 = 2.0*mMax1/3.0 + mMax1/10.0
        mMax2 = mMax1/3.0
        mMin2 = mMax1/6.0
        
        # Find value for first T2 (=p(1))
        index_mMin1 = np.nonzero(data > mMin1)
        mExp1    = data[index_mMin1[0][9:]]
        timeFit1 =    t[index_mMin1[0][9:]]
        
        y = np.log(mExp1)
        x = timeFit1
        p = np.polyfit(x, y, 1.)
        
        # Find value for first T2 (=x(2))
        index_mMin2a = np.nonzero(data > mMin2)
        index_mMin2b = np.nonzero(data < mMax2)
        range_index = np.array([n for n in np.arange(len(data)) if ((n in index_mMin2a[0]) and (n in index_mMin2a[0]))])
        mExp2 = data[range_index]
        
        timeFit2 = t[range_index]
        if len(mExp2) > 40:
            mExp2 = mExp2[0:40]
            timeFit2 = timeFit2[0:40]
    
        # Find value for second T2 (=q(1))
        y = np.log(mExp2)
        x = timeFit2
        q = np.polyfit(x, y, 1.)
    
        mT21 = -1.0/p[0]
        mT22 = -1.0/q[0]
        mk = mT21/mT22
        mexp = 1.0 - mk
        if mT21 > mT22:
            mT2used = lwfact * mT21
        else:
            mT2used = lwfact * mT22 * mk**mexp
            
        #*********************************
        # Divide ideal into actual to obtain amplitude correction (mConAmpCor)
        # Phase correction is just negative of dcy phase (mSPhase)
        
        mSideal = np.exp(-t/mT2used)
        aMs = np.max(data)
        mConAmpCor = aMs*mSideal/data
    
        iterr = 0
        if np.max(mConAmpCor) > aCorrMax:
            maxCorr = np.max(mConAmpCor)
            while maxCorr > aCorrMax:
                # Add small amount of 2 Hz line to data (do this at most twice)
                if iterr < 2:
                    data = data + 0.01*aMs*np.exp(-t*2*np.pi) ;
                # Make T2used shorter if AmpCor exceeds maximum (aCorrMax)  
                mT2used = mT2used - 0.001
                mSideal= np.exp(-t/mT2used) ;
                mConAmpCor = aMs*mSideal/data
                maxCorr = np.max(mConAmpCor)
                iterr += 1
        
        mSPhase = np.unwrap((-np.angle(dcy)))
        
        # Filter amp and phase, and limit amp
        mConAmpCor = self._savitzky_golay(self._savitzky_golay(mConAmpCor, 11, 5), 9, 4)
        mSPhase    = self._savitzky_golay(mSPhase, 9, 3)
        
        npts1 = len(t)
        npts2 = (1.4/npts1)*np.arange(npts1)
        mExpMul    = np.exp((-npts2**12.0))
        mConAmpCor = mConAmpCor*mExpMul
    
        return [mConAmpCor, mSPhase, mT2used]
    
    
    def _refdecb_gm(self, dcy, mConAmpCor, mSPhase, mT2used, sw):
        """
        _refdecb_gm(metab_fid,Ampcor,Phasecor,T2E)
    
        Uses amp and phase corrections from water only signal
        ti deconvolve a metabolite FID - aprroximates Lorentzian line
        shapes for the metabolite lines. It further applies a TRAF filter
        to improve the lineshape.
        
        Input:
           metab_fid - a metabolite FID
           Ampcor - amplitude correction to multiply metabolite FID by
           Phasecor - phase correction to use on metabolite FID (length
                      of FID)
           T2E - T@ estimated from water reference FID
        Output:
           corrected meatbolite FID
           
        """
        t2e = mT2used
    
        # FIRST APPLY AMP AND PHASE CORRECTIONS ************
        # Work with absolute mode to obtain T2 estimate
        # Fits to beginning and end of FID (absolute mode)
        data = np.abs(dcy)
        data[0] = 2.0*data[0]
        
        # Amp correction
        data = data*mConAmpCor
        
        # Phase correction
        phasea = np.angle(dcy)+mSPhase
        
        # Corrected data
        dcy = data*np.exp(np.complex(1j)*phasea)
        
        #********************************************
        # NOW APPLY TRAF FILTER FROM ROUTINE TRAF_GM
        siglen = len(dcy)
        traffilter = self._traf_gm(siglen, t2e, sw)
        
        realdcy = dcy*traffilter.real + (dcy*traffilter.real)[::-1]
        imagdcy = dcy*traffilter.imag - (dcy*traffilter.imag)[::-1]
        dcy = 0.5 * (realdcy + imagdcy)
        
        # Halve first pt prior to FT
        dcy[0] = dcy[0]/2.0
        
        return dcy     
  
