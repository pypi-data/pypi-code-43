# Python modules
from __future__ import division

# Function for filtering/smoothing a pulse. 
# e.g. for diminishing "Conolly wings"
# Uses Savitzky-Golay coefficients
    
def sg_smooth(data, npoints, niterations):
    '''
    Function for smoothing Connelly wings and other artifacts,
    at the beginning and end of the pulse. Uses Savitzky-Golay 
    coefficients, and includes 5 points in the smoothing algorithm.
    
    data: The raw Waveform data.
    npoints: The number of points on either end to smooth.
    niterations: How many times to perform the smoothing.
    '''
    
    n = len(data)
    
    for m in range(niterations):

        for k in range(npoints):
        
            data[k] =  .886*data[k] + .257*data[k+1] \
                    -.086*data[k+2]-.143*data[k+3]+.086*data[k+4]
        
            data[n-1-k] =  .886*data[n-k-1] + .257*data[n-k-2] \
                        -.086*data[n-k-3]-.143*data[n-k-4]+.086*data[n-k-5]
        

