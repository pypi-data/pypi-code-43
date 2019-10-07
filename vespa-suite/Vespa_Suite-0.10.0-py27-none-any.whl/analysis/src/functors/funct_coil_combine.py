# Python imports
from __future__ import division

# 3rd party imports
import numpy as np
import scipy

# Vespa imports



COILCOMBINE_MENU_ITEMS = ['Siemens', 'CMRR', 'CMRR-Sequential', 'CMRR-Hybrid', 'External Dataset', 'External Dataset with Offset']


 
 

def coil_combine_siemens(chain):
    """ 
    Combine code from IceSpectroEdit program, a la Mark Brown 
    
    Given a list of scans and the extracted parameter dictionary we process
    the data in as similar a way to Siemens ICE program IceSpectroEdit as
    we can. My way of removing oversampling seems to not match 100% but the
    other steps are in the order and perform very similarly to the ICE program.
    
    Note. Since this got moved out of the Import step, we are assuming that 
    the following processing steps have already been applied:
      1. oversampling removal 
      2. global scaling to reasonable numerical range
      3. (optional) complex conjugate for proper display

    Input data is array with (1, ncoils, nfids, npts) dimensions
    Output data array has    (1,      1, nfids, npts) dimension

    Output ndarray collapses ncoils dimension by combining each group of ncoils
    FIDs into a weighted/phased summed FID. 
    
    Other Output:
    
    all_weight   ndarray[nfids,ncoils], float, weights calculated/used to combine 
                   each group of ncoil FIDs into a single FID 

    all_phases   ndarray[nfids,ncoils], complex, phases calculated/used to combine 
                   each group of ncoil FIDs into a single FID 
    
    """
    block   = chain._block
    set     = chain._block.set
    dataset = chain._dataset
    raw     = chain.raw

    dim0    = raw.shape[3]
    acqdim0 = dim0
    nfids   = raw.shape[2]
    ncoils  = raw.shape[1]
    
    flag_norm_to_sum = False                    # default for now

    dat_comb = np.ndarray([nfids,dim0], dtype=np.complex128)
   
    # Parse each group of FIDs for N channels for each average as separate
    # from all other scans. Perform the following steps:
    # - accumulate weighting factors and phases, all channels
    # - collate all channels as numpy arrays
    # - calc final weights for each channel 
    # - apply weight and phase corrections to all channels

    all_weight = np.ndarray([nfids,ncoils], dtype=np.float)
    all_phases = np.ndarray([nfids,ncoils], dtype=np.complex)

    for i in range(nfids):
        
        # for each average, calc phase and weights to correct for coil geometry
        chans  = []
        weight = []
        phases = []
        
        for j in range(ncoils):
            chan = chain.raw[0,j,i,:].copy() 
            magn = np.abs(chan[0])
            phas = np.conjugate(chan[0])/magn        # normalized complex conj to cancel phase

            phases.append(phas)
            weight.append(magn)
            chans.append(chan) 
            
        # normalize weighting function based on spectro data 
        tmp = np.sum([val*val for val in weight])   # sum squared values         
        if tmp == 0.0: tmp = 1.0
        if flag_norm_to_sum:
            # sum of sensitivities
            lamda = np.sum(weight) / tmp  
        else:
            # sqrt of sum of squared sensitivities
            lamda = 1.0 / np.sqrt(tmp)
        
        weight = [wt*lamda for wt in weight]
        
        all_weight[i,:] = weight
        all_phases[i,:] = phases
        
        # apply weighting and phase corrections
        for j,chan in enumerate(chans):
            chans[j] = chan * weight[j] * phases[j]
        
        # sum corrected FIDs from each coil into one combined FID
        dat_comb[i,:] = np.sum(chans, axis=0) 

    print_combine_stats(all_weight, all_phases, method='Siemens') 
        
    return normalize_shape(dat_comb), all_weight, all_phases
  

def coil_combine_cmrr_sequential(chain):
    """ 
    Combine method hybrid of Siemens and Gulin Oz CMRR
    
    Derived from Matlab code from Dinesh. The coil weights and phases are 
    calculated from each scan in the scan list as in CMRR code, but are then
    applied only to its own scan as in the Siemens code.

    Input data is array with (1, ncoils, nfids, npts) dimensions
    Output data array has    (1,      1, nfids, npts) dimension

    Output ndarray collapses ncoils dimension by combining each group of ncoils
    FIDs into a weighted/phased summed FID. 
    
    Other Output:
    
    all_weight   ndarray[nfids,ncoils], float, weights calculated/used to combine 
                   each group of ncoil FIDs into a single FID 

    all_phases   ndarray[nfids,ncoils], complex, phases calculated/used to combine 
                   each group of ncoil FIDs into a single FID 
   
    """
    block   = chain._block
    set     = chain._block.set
    dataset = chain._dataset
    raw     = chain.raw

    ncoils  = raw.shape[1]
    nfids   = raw.shape[2]
    dim0    = raw.shape[3]
    acqdim0 = dim0
    xaxis   = range(dim0)

    flag_norm_to_sum = False                    # default for now

    dat_comb = np.ndarray([nfids,dim0], dtype=np.complex128)

    all_weight = np.ndarray([nfids,ncoils], dtype=np.float)
    all_phases = np.ndarray([nfids,ncoils], dtype=np.complex)

    for i in range(nfids):

        # determine weighting and phz for each coil
        #   zero-order phase correction
        #   correct for phase based on 1st point in 1st wref fid

        # for each average, calc phase and weights to correct for coil geometry
        chans  = []
        weight = []
        phases = []
        
        for j in range(ncoils):
            chan = chain.raw[0,j,i,:].copy()
            
            magn = np.abs(chan[0])
            phas = np.conjugate(chan[0])/magn        # normalized complex conj to cancel phase        
            chan = phas * chan                       # Note. applying phase here NOT below as in Siemens
        
            # amplitude of zero order phased fid in time domain
            #   using 9th order polynomial fit (based on  Uzay's script)
            coeffs = np.polyfit(xaxis, np.absolute(chan), 9)
            
            weight.append(coeffs[-1])       # last entry is amplitude - zero order coeff
            phases.append(phas)
            chans.append(chan)
        
        # normalize weighting function based on spectro data 
        tmp = np.sum([val*val for val in weight])   # sum squared values         
        if tmp == 0.0: tmp = 1.0
        if flag_norm_to_sum:
            # sum of sensitivities
            lamda = np.sum(weight) / tmp  
        else:
            # sqrt of sum of squared sensitivities
            lamda = 1.0 / np.sqrt(tmp)

        weight = [val*lamda for val in weight]

        all_weight[i,:] = weight
        all_phases[i,:] = phases
        
        # apply weighting ... phase corrections done above
        for j,chan in enumerate(chans):
            chans[j] = chan * weight[j]
        
        # sum corrected FIDs from each coil into one combined FID
        dat_comb[i,:] = np.sum(chans, axis=0) 

    print_combine_stats(all_weight, all_phases, method='CMRR_Sequential')
        
    return normalize_shape(dat_comb), all_weight, all_phases 


def coil_combine_cmrr(chain, delta=0.0):
    """ 
    Coil combine method from Gulin Oz at CMRR 
    
    Derived from Matlab code from Dinesh. The coil weights and phases are 
    calculated once from the first scan in the scan list, then these values
    are applied globally to all subsequent scans.

    Input data is array with (1, ncoils, nfids, npts) dimensions
    Output data array has    (1,      1, nfids, npts) dimension

    Output ndarray collapses ncoils dimension by combining each group of ncoils
    FIDs into a weighted/phased summed FID. 
    
    Other Output:
    
    all_weight   ndarray[nfids,ncoils], float, weights calculated/used to combine 
                   each group of ncoil FIDs into a single FID 

    all_phases   ndarray[nfids,ncoils], complex, phases calculated/used to combine 
                   each group of ncoil FIDs into a single FID 
    
    """
    block   = chain._block
    set     = chain._block.set
    dataset = chain._dataset
    raw     = chain.raw

    ncoils  = raw.shape[1]
    nfids   = raw.shape[2]
    dim0    = raw.shape[3]
    acqdim0 = dim0
    xaxis   = range(dim0)

    flag_norm_to_sum = False                    # default for now

    dat_comb = np.ndarray([nfids,dim0], dtype=np.complex128)

    all_weight = np.ndarray([nfids,ncoils], dtype=np.float)
    all_phases = np.ndarray([nfids,ncoils], dtype=np.complex)

    weight = []
    phases = []

    #--------------------------------------------------------------------------
    # Calc weights and phases from first scan only 
   
    for j in range(ncoils):
        chan = chain.raw[0,j,0,:].copy()
        
        magn = np.abs(chan[0])
        phas = np.conjugate(chan[0])/magn        # normalized complex conj to cancel phase        
        chan = phas * chan
    
        # amplitude of zero order phased fid in time domain
        #   using 9th order polynomial fit (based on  Uzay's script)
        coeffs = np.polyfit(xaxis, np.absolute(chan), 9)
        
        weight.append(coeffs[-1])       # last entry is amplitude - zero order coeff
        phases.append(phas)
    
    #--------------------------------------------------------------------------
    # normalize weighting function based on spectro data 

    tmp = np.sum([val*val for val in weight])   # sum squared values         
    if tmp == 0.0: tmp = 1.0
    if flag_norm_to_sum:
        # sum of sensitivities
        lamda = np.sum(weight) / tmp  
    else:
        # sqrt of sum of squared sensitivities
        lamda = 1.0 / np.sqrt(tmp)

    weight = [val*lamda for val in weight]

    global_weight = np.array(weight)
    global_phases = np.array(phases) + delta


    #--------------------------------------------------------------------------
    # Apply weights and phases from first scan to all scans

    for i in range(nfids):

        # apply pre-calculated phase and weights
        chans  = []
        for j in range(ncoils):
            chan = chain.raw[0,j,i,:].copy()
            chan = chan * global_phases[j] * global_weight[j]
            chans.append(chan)
        
        # sum corrected FIDs from each coil into one combined FID
        dat_comb[i,:] = np.sum(chans, axis=0) 

        all_weight[i,:] = global_weight
        all_phases[i,:] = global_phases 

    print_combine_stats(all_weight, all_phases, method='CMRR')
        
    return normalize_shape(dat_comb), all_weight, all_phases


def coil_combine_external_dataset(chain, delta=0.0):
    """ 
    Coil combine method that uses values calculated in another dataset.
    
    Input data is array with (1, ncoils, nfids, npts) dimensions
    Output data array has    (1,      1, nfids, npts) dimension

    Output ndarray collapses ncoils dimension by combining each group of ncoils
    FIDs into a weighted/phased summed FID. 
    
    Other Output:
    
    all_weight   ndarray[nfids,ncoils], float, weights calculated/used to combine 
                   each group of ncoil FIDs into a single FID 

    all_phases   ndarray[nfids,ncoils], complex, phases calculated/used to combine 
                   each group of ncoil FIDs into a single FID 
    
    In some cases we want to use the coil_combine results from a single high
    SNR water FID to combine multiple low SNR metabolite FIDs. In this case 
    we create weight and phase arrays that are nfids copies of the 1,ncoils 
    array of weight and phase values from the external data set.
    
    """
    block   = chain._block
    set     = chain._block.set
    dataset = chain._dataset
    raw     = chain.raw

    dim0    = raw.shape[3]
    acqdim0 = dim0
    nfids   = raw.shape[2]
    ncoils  = raw.shape[1]

    dat_comb = np.ndarray([nfids,dim0], dtype=np.complex128)
    all_weight  = set.coil_combine_weights.copy()     
    all_phases  = set.coil_combine_phases.copy() * np.exp(1j*delta)

    # expand/copy weights/phases if nfids dimension differs from raw data here
    if all_weight.shape[0] != nfids:
        all_weight = np.tile(all_weight[0], nfids)
        all_weight.shape = (nfids, ncoils)
    if all_phases.shape[0] != nfids:
        all_phases = np.tile(all_phases[0], nfids)
        all_phases.shape = (nfids, ncoils)

    for i in range(nfids):
        # apply pre-calc phase and weights to correct for coil geometry
        chans  = []
        for j in range(ncoils):
            data    = chain.raw[0,j,i,:].copy()
            weights = all_weight[i,j]
            phases  = all_phases[i,j]
            chans.append( data * weights * phases ) 
        
        # sum corrected FIDs from each coil into one combined FID
        dat_comb[i,:] = np.sum(chans, axis=0) 

    print_combine_stats(all_weight, all_phases, method='External Dataset')
        
    return normalize_shape(dat_comb), all_weight, all_phases 



def coil_combine_none(chain):
    """ here we just copy data from first coil channel """

    dat_comb = chain.raw[0,0,:,:].copy()
    return normalize_shape(dat_comb)


def normalize_shape(item):
    """ 
    'item' should be a numpy ndarray. Our convention is for Vespa MRS data
    to have 4 dimensions. This function returns 'item' with a 4 dimesional 
    shape array (x, ncoils, nfids, npts) regardless of how many dimensions
    it had coming in. 
    
    """
    padding = 4 - len(item.shape)  #len(DataRaw.DEFAULT_DIMS)
    if padding > 0:
        item.shape = ([1] * padding) + list(item.shape)
    return item




def do_coil_combine_processing(chain):
    
    method = chain._block.set.coil_combine_method
    
    if method == 'Siemens':
        coil_combine_siemens(chain)
        
    elif method == 'Hamming - water filter':
        coil_combine_cmrr(chain)
        
        


#------------------------------------------------------------------------------
# Helper Functions

def print_combine_stats(all_weight, all_phases, method=''):
    #pass
    return
    # take mean values for all fids on one coil 
    mean_weight = np.mean(all_weight, axis=0)
    mean_phases = np.angle(np.mean(all_phases, axis=0), deg=True) 
    stdv_weight = np.std(all_weight, axis=0)
    stdv_phases = np.std(np.angle(all_phases, deg=True), axis=0)

#    print '\n'
#    print method+" Weights mean      = \n", mean_weight
#    print method+" Weights ratios = \n", ["{0:0.2f}".format(i/max(abs(mean_weight))) for i in mean_weight]
#    print method+" Weights % stdv    = ", 100.0*stdv_weight/mean_weight
#    print method+" Phases [deg] mean = \n", mean_phases 
#    print method+" Phases [deg] mean = \n", ["{0:0.2f}".format(i) for i in mean_phases]
#    print method+" Phases % stdv     = ", 100.0*stdv_phases/mean_phases    



'''
function varargout = weightsmod(varargin)
% function varargout = weightsmod(varargin)
% determine and apply weighting Factor for each coil
% method = 1, determine weighting and phz for each coil
% method = 2, apply weights and phz to data
%
% Dinesh Deelchand, 18 March 2013

if (nargin < 2)
    method = 1;
    fidw = varargin{1};
elseif (nargin == 3)
    method = 2;
    fiduse = varargin{1};
    wk = varargin{2};
    refphz =  varargin{3};
else
    errorbox('Number of input parameters is not valid in weightsmod','warn')
    return
end

if (method == 1)
    %% determine weighting and phz for each coil
    % zero-order phase correction
    % correct for phase based on 1st point in 1st wref fid
    [np,nbCoils] = size(fidw);
    fidwphz = complex(zeros(size(fidw)));
    refphz = zeros(nbCoils,1);
    for iy = 1:nbCoils
        refphz(iy) = angle(fidw(1,iy));
        fidwphz(:,iy) = phase_adjust(fidw(:,iy),refphz(iy));
    end
    
    % weighting factor
    fidecc = squeeze(fidwphz(:,:));
    
    % amplitude of fid in time domain
    % using 9th order polynomial fit (based on  Uzay's script)
    warning off MATLAB:polyfit:RepeatedPointsOrRescale
    pts =(1:np)';
    amplfid = zeros(nbCoils,1);
    for ical = 1:nbCoils
        wktemp = polyfit(pts,abs(double(fidecc(:,ical))),9);
        amplfid(ical) = wktemp(end); % last entry is amplitude
        
        % show fit
        %f=polyval(wktemp,pts);
        %figure, plot(abs(double(fidecc(:,ical))));
        %hold on, plot(f,'r');
    end
    
    % weighting function
    wk = amplfid/sqrt(sum(amplfid.^2));
    
    % return variables
    varargout{1} = wk;
    varargout{2} = refphz;
    
elseif (method == 2)
    %% apply weights and phz to data
    if (ndims(fiduse) == 2) %2D size
        
        fiduse_phz = complex(zeros(size(fiduse)));
        nbCoils = size(fiduse,3);
        
        % zero-order phase correction
        for iy = 1:nbCoils
            fiduse_phz(:,iy) = phase_adjust(fiduse(:,iy),refphz(iy));
        end
        
        % apply weightings
        fidweighted = complex(zeros(size(fiduse_phz)));
        for ical=1:length(wk)
            fidweighted(:,ical) = wk(ical).*fiduse_phz(:,ical);
        end
        
        %sum all channels
        sumfidweighted = sum(fidweighted,2);
        
    elseif (ndims(fiduse) == 3)   %3D size
        
        fiduse_phz = complex(zeros(size(fiduse)));
        nbCoils = size(fiduse,3);
        nt = size(fiduse,2);
        
        % zero-order phase correction
        for iy = 1:nbCoils
            for ix = 1:nt
                fiduse_phz(:,ix,iy) = phase_adjust(fiduse(:,ix,iy),refphz(iy));
            end
        end
        
        % apply weightings
        fidweighted = complex(zeros(size(fiduse_phz)));
        for ical=1:length(wk)
            fidweighted(:,:,ical) = wk(ical).*fiduse_phz(:,:,ical);
        end
        
        %sum all channels
        sumfidweighted = sum(fidweighted,3);
    end
    
    % return variables
    varargout{1} = sumfidweighted ;
end
return


function outfid = phase_adjust(trc, phase)
% function to apply phase angles to complex data, e.g. to use
% variable receiver phases in VNMR

rtrc = real(trc);
itrc = imag(trc);

cosp = cos(phase); % real_cor
sinp = sin(phase); % imag_cor

rout = rtrc.*cosp + itrc.*sinp;
iout = itrc.*cosp - rtrc.*sinp;

outfid = complex(rout, iout);
return

'''


