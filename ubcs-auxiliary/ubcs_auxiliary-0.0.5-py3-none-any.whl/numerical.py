"""
plotting functions
author: Valentyn Stadnytskyi
data: 2017 - Nov 17 2018

"""
__vesrion__ = '1.0.0'
from time import  time, sleep
import sys
if sys.version_info[0] == 2:
    from time import clock as perf_counter
else:
    from time import perf_counter
import platform
from numpy import asarray

def exponential_1(x,A,tau):
    from numpy import exp
    return A*exp(-x/tau)

def linear(x,a,b):
    return a + b*x

def binary_to_array(value = 0, length = 8):
    """
    takes an integer and converts it to 8 bit representation as an array.
    If float number is passed, it will be converted to int.
    """
    from numpy import arange,ndarray,nan
    value = int(value)
    binary = format(value, '#0'+str(length+2)+'b')
    arr = arange(length-1)
    for i in range(length-1):
        arr[i] = binary[length+1-i]
    return arr

def array_to_binary(arr = asarray([ 1,  1,  1,  1,  1,  1,  1])):
    """
    takes an integer and converts it to 8 bit representation as an array.
    If float number is passed, it will be converted to int.
    """
    from numpy import arange,ndarray,nan
    integer = 0
    for i in range(len(arr)):
        integer += int(arr[i]*2**(i))
    return integer

def bin_data(data  = None, x = None, axis = 1, num_of_bins = 300, dtype = 'float'):
        """returns a vector of integers on logarithmic scale starting from decade start, ending decade end with M per decade
        Parameters
        ----------
        data (numpy array)
        x_in (numpy array)
        axis (integer)
        num_of_bins (integer)
        dtype (string)

        Returns
        -------
        dictionary with keys: 'x',y_min','y_max''y_mean'

        Examples
        --------
        >>> from numpy import random, arange
        >>> data = random.rand(4,1000)+ 1
        >>> x_in = arange(0,data.shape[0]+1,1)
        >>> binned_data = bin_data(data  = None, x_in = None, axis = 1, num_of_bins = 300, dtype = 'float')

        .. plot:: ./examples/numerical_bin_data.py
           :include-source:

        """
        from numpy import zeros, nan,arange, nanmax, nanmin, random,nanmean, mean
        import math

        length = data.shape[0]
        width = data.shape[1]

        if length <= num_of_bins:
            y_max = data
            y_min = data
            y_mean = data
            x_out = x
        else:
            y_min = zeros(shape = (width,num_of_bins), dtype = dtype)
            y_max = zeros(shape = (width,num_of_bins), dtype = dtype)
            y_mean = zeros(shape = (width,num_of_bins), dtype = dtype)
            x_out = zeros(shape = (num_of_bins,), dtype = dtype)

            for j in range(width):
                idx = 0
                for i in range(num_of_bins):
                    step = int(math.ceil(1.0*(length - idx)/(num_of_bins-i)))

                    start = idx
                    end = idx + step
                    if 'int' in dtype:
                        y_max[j,i] = int(nanmax(data[start:end,j]))
                        y_mean[j,i] = int(nanmean(data[start:end,j]))
                        y_min[j,i] = int(nanmin(data[start:end,j]))
                    else:
                        y_max[j,i] = nanmax(data[start:end,j])
                        y_mean[j,i] = nanmean(data[start:end,j])
                        y_min[j,i] = nanmin(data[start:end,j])
                    x_out[i] = mean(x[start:end])
                    idx += step
        dic = {}
        dic['x'] = x_out
        dic['y_min'] = y_min
        dic['y_max'] = y_max
        dic['y_mean'] = y_mean
        return dic

def sort_vector(in_vector = asarray([ 1,  1,  1,  1,  1,  1,  1])):
    """sorts time vector"""
    from numpy import sort
    if in_vector.ndim == 1:
        out_vector = sort(in_vector)
    return out_vector

def expand_vector(in_vector = asarray([ 1,  1,  1,  1,  1,  1,  1]),ndim = 2):
    """ makes input 1D vector as 2D with first dimenstion to be ndim"""
    from numpy import zeros,expand_dims,concatenate
    out_vector = expand_dims(in_vector, axis = 0)
    add_vector = out_vector*0
    for i in range(ndim-1):
        out_vector = concatenate((out_vector,add_vector),axis=0)
        return out_vector

def get_estimate(x,y,x_est, order = 2):
        """
        returns estimated y_est value for give x_est from real x,y data set.
        """
        from numpy import polyfit, poly1d, nanargmin
        idx = nanargmin((x - x_est)**2)
        x0 = x[idx]
        debug('x = %r' %x)
        debug('y = %r' %y)
        debug('x_est = %r' %y)
        debug('idx = %r' %idx)
        debug('x0 = %r' %x0)
        if len(x) !=0 or len(y) != 0:
            fit = polyfit(x-x0,y,order)
            ynew_fit = poly1d(fit)(x_est-x0)
        else:
            ynew_fit = nan
        return ynew_fit

def log_scale(N = 8, start = -9, end = 3, round_to = 3):
    """creates an array of numbers on logarithmic scale with:
        - number per decade
        - start decade
        - end decade
        - round_to number of digits after decimal, default is 3
        """
    from numpy import logspace, around
    arr = around(logspace(start,  end, (end-start)*N+1, endpoint=True),abs(start-round_to))
    return arr

def local_log_scale(start_dec, end_dec, N_per_dec, dtype = 'int64'):
    """returns a vector of integers on logarithmic scale starting from decade start, ending decade end with M per decade
    Parameters
    ----------
    start_dec (integer)
    end_dec (integer)
    N_per_dec (integer)
    dtype (string)

    Returns
    -------
    array (numpy array)

    Examples
    --------
    >>> arr = local_log_scale(start_dec = -9, end_dec = 1, N_per_dec = 4, dtype = 'int64')
    """
    from numpy import logspace, around
    arr = logspace(start_dec,  end_dec, (end_dec-start_dec)*N_per_dec, endpoint=False,dtype = dtype)
    return arr

def bin_on_logscale(x,y,N = 100, dN = 1, x0 = 0, M = 16, order = 1, mode = 'polyfit'):
    """
    purpose: binning of data: first N points starting from x0 are
    binned in bins of size dN and the rest is binned on logarithmic scale with M per decade

    Parameters
    ----------
    x (integer) - x-axis of data
    y (integer) - y-axis of data
    x0 (float) - the zero on x-axis
    N (int) - number of points after x0 that are binned , dN bi size, on linear scale
    dN (integer) - size of the bin for the linear scale, first N points.
    M (integer)- number of points per decade for the rest of the data

    Returns
    -------
    (y_mean, y_std, x_out, num)
    y_mean array (numpy array)
    y_std  array (numpy array)
    x_out  array (numpy array)
    num array (numpy array)

    Examples
    --------
    >>> arr = local_log_scale(start_dec = -9, end_dec = 1, N_per_dec = 4, dtype = 'int64')
    """
    if M >128:
        raise ValueError('Value of M = %r has exceeded allowed (%r)' %(M,128))

    def lin_func(x_l,x_r,y,x0, order = 2, fit_mode = 'mean'):
        """
        """
        from numpy import polyfit, poly1d, arange, std
        if y.shape[0] > 1:
            x = arange(x_l,x_r,1)
            if x.shape[0] >2:
                if fit_mode == 'polyfit':
                    #print('1',fit_mode)
                    y_fit = poly1d(polyfit(x,y,deg = order))
                    y_fit_x0 = y_fit(x0)
                    y_std = (sum((y_fit(x) - y)**2)/x.shape[0])**0.5
                elif fit_mode == 'bevington':
                    #print('2',fit_mode)
                    a,b,y_std = linear_fit(x,y)
                    y_fit_x0 = linear(x0,a,b)
                else:
                    #print('3',fit_mode)
                    y_fit_x0,y_std = mean(y), std(y)
            else:
                if fit_mode == 'polyfit':
                    y_fit = poly1d(polyfit(x,y,deg = 1))
                    y_fit_x0 = y_fit(x0)
                    y_std = (sum((y_fit(x) - y)**2)/x.shape[0])**0.5
                elif fit_mode == 'bevington':
                    a,b,y_std = linear_fit(x,y)
                    y_fit_x0 = linear(x0,a,b)
                else:
                    y_fit_x0,y_std = mean(y), std(y)


            return y_fit_x0, y_std
        else:
            return y, 0
    t={}
    k = 0
    t0 = time()

    from numpy import mean, std, arange, argwhere, concatenate,polyfit, poly1d, mod, log10
    y = transpose(y)
    x_len = x.shape[0]
    y_len = y.shape[0]
    num = x_len
    t[k] = time() - t0;k +=1;
    lin_left = arange(0,(N-1)*dN,dN)
    lin_right = arange(dN,N*dN,dN)
    lin_middle = lin_left/2.0+(lin_right-1)/2.0
    #print('lin_left.shape[0] = %r. lin_right.shape[0] = %r' %(lin_left.shape[0], lin_right.shape[0]))
    t[k] = time() - t0;k +=1;
    up_to = int(log10(num))+1
    x_log = local_log_scale(1,up_to,2*M)
    arr1  = x_log[argwhere((x_log >= lin_right[-1]))][:,0]
    arr2 = arr1[argwhere(arr1 <= x_len)][:,0]
    log_left = arr2[asarray(range(0,arr2.shape[0],2))]
    log_middle = arr2[asarray(range(1,arr2.shape[0],2))]
    log_right = arr2[asarray(range(2,arr2.shape[0],2))]
    t[k] = time() - t0;k +=1;
    right = concatenate((lin_right,log_right))
    left = concatenate((lin_left,log_left))[:len(right)]
    middle = concatenate((lin_middle,log_middle))[:len(right)]

    t[k] = time() - t0;k +=1;
    x_out = right*0.0
    y_mean = right*0.0
    y_std = right*0.0
    num = right*0.0
    #print(bogus)
    t[k] = time() - t0;k +=1;
    for i in range(x_out.shape[0]):
        #if mod(N,2):
        x_out[i],x_out_std = lin_func(left[i],right[i],x[left[i]:right[i]],middle[i], order = order, fit_mode = 'polyfit')
        #else:
           # try: x_out[i] = x[int(middle[i])]
           # except: print('bla');x_out[i] = x[int(middle[i])-1]
        y_mean[i],y_std[i] = lin_func(left[i],right[i],y[left[i]:right[i]],middle[i], order = order, fit_mode = mode)
        num[i] = x[left[i]:right[i]].shape[0]
    t[k] = time() - t0;k +=1;
    return y_mean, y_std, x_out, num


def linear_fit(x,y):
    """
    return linear fit by calcualating
    y_fit = a + b*x
    page 104 Data reduction and error analysis for the physicxal sciences Philip R. Bevington

    Parameters
    ----------
    x (1d numpy array)
    y (1d numpy array)

    Returns
    -------
    a
    b
    sigma

    Examples
    --------
    >>> a, b , sigma = linear_fit(x,y)
    """

    from numpy import isnan,nan, sum

    Sx = sum(x*1.0) #Sx_i = Sx_i-1 +x_i
    Sx2 = sum(x**2.00) #Sx2_i = Sx2_i-1 + x_i**2
    Sy = sum(y*1.0) #Sy_i = Sy_i-1 + y_i
    Sy2 = sum(y**2.0) #Sy2_i = Sy2_i-1 + y_i**2
    Sxy = sum(x*y*1.0) #Sxy_i = Sxy_i-1 + x_i*y_i
    N = x.shape[0]#N_i = N_i-1 + 1.0
    if N >= 2:
        Delta = N*Sx2 - Sx**2 # Delta_i = N_i*Sx2_i - Sx_i**2
        a = (1.0/Delta)*(Sx2*Sy-Sx*Sxy)
        b = (1.0/Delta)*(N*Sxy-Sx*Sy)
    else:
        a = None
        b = None
        #page 115
    if N > 2:
        Sigma = (1/(N-2))*(Sy2+N*a**2+(b**2)*Sx2-2*a*Sy-2*b*Sxy+2*a*b*Sx)
    else:
        Sigma = None

    return a, b, Sigma



if __name__ == '__main__':
    from matplotlib import pyplot as plt
    from numpy import random, arange
    from pdb import pm
    data = random.rand(1000,4)+ 1
    x = arange(0,data.shape[0],1)
    binned_data = bin_data(data  = data, x = x, num_of_bins = 300, dtype = 'float')
    plt.plot(binned_data['x'],binned_data['y_mean'][0],'o')
    plt.plot(x,data[:,0],'-')
    plt.show()
