# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

def time_series_forecast(x, p, nvalues, backcast=False, reflect=False):
    """
    This function computes future or past values of a stationary time-
    series (X) using a Pth order autoregressive model. The result is an
    nvalues-element numpy array whose type is identical to X.

    This function uses the last P elements [Xn-1, Xn-2, ... , Xn-p]
    of the time-series [x0, x1, ... , xn-1] to compute the forecast.
    More coefficients correspond to more past time-series data used
    to make the forecast.

    x   An n-element numpy array of floats containing time-series data

    p   A scalar othat specifies the number of actual time-series values 
        to be used in the forecast. In general, a larger number of values 
        results in a more accurate result.

    nvalues    A scalar that specifies the number of future or past 
               values to be computed.

    backcast   If set then "backcasts" (backward-forecasts)are computed

    Based on ...
    The Analysis of Time Series, An Introduction (Fourth Edition)
    Chapman and Hall  ISBN 0-412-31820-2

    """
    nvalues = int(nvalues)

    if nvalues <= 0:
        raise ValueError, "nvalues must be a scalar > 0"

    nx = len(x)

    if p<2 or p>(nx-1):
        raise ValueError, "p must be a scalar in  [2, len(x)-1]"

    # reverse time-series for backcasting.
    if backcast:
        x = x[::-1]

    # last p elements of time-series.
    data = (x[nx-int(p):])[::-1]

    fcast = np.zeros(nvalues, float)

    # compute coeffs
    arcoeff = time_series_coef(x, int(p))

    for j in np.arange(nvalues):
        data = np.concatenate((np.array([(data * arcoeff).sum()]), data[0:int(p)-1]))
        fcast[j] = data[0]

    if backcast:
        return fcast[::-1]
    else:
        return fcast


def time_series_coef(x, p):
    """
    This function computes the coefficients used in a Pth order
    autoregressive time-series forecasting/backcasting model. The
    result is a P-element numpy array 

    Used to compute the coefficients of the Pth order autoregressive 
    model used in time-series forecasting/backcasting.
    arcoef = arcoef[0, 1, ... , p-1]

      x:    An n-element vector of type float or double containing time-
            series samples.

      p:    A scalar of type integer or long integer that specifies the
            number of coefficients to be computed.

    mse:    calculates the mean square error of the Pth order 
            autoregressive model

    Based on ...
    
    The Analysis of Time Series, An Introduction (Fourth Edition)
    Chapman and Hall
    ISBN 0-412-31820-2
    
    """

    nx = len(x)

    if p<2 or p>(nx-1):
        msg = "p must be a scalar in [2, len(x)-1]"
        return

    mse = (x*x).sum() / nx

    arcoef = np.zeros(p, float)
    str1 = np.concatenate((np.array([0.0]), x[0:nx], np.array([0.0])))
    str2 = np.concatenate((np.array([0.0]), x[1:],   np.array([0.0])))
    str3 = np.zeros(nx+1, float)

    for k in np.arange(p)+1:
        arcoef[k-1] = 2.0*(str1[1:nx-k+1] * str2[1:nx-k+1]).sum() / (str1[1:nx-k+1]**2 + str2[1:nx-k+1]**2).sum()

        mse = mse * (1.0 - arcoef[k-1]**2)

        if k>1:
            for i in np.arange(k-1)+1:
                arcoef[i-1] = str3[i] - (arcoef[k-1] * str3[k-i])

        # if k == p then skip the remaining calcs
        if k == p:
            break
            
        str3[1:k+1] = arcoef[0:k]
        for j in np.arange(nx-k-1)+1:
            str1[j] = str1[j]   - str3[k] * str2[j]
            str2[j] = str2[j+1] - str3[k] * str1[j+1]
    
    return arcoef



if __name__ == '__main__':

    # Test Forecast
    x = np.array([6.63, 6.59, 6.46, 6.49, 6.45, 6.41, 6.38, 6.26, 6.09, 5.99, \
                  5.92, 5.93, 5.83, 5.82, 5.95, 5.91, 5.81, 5.64, 5.51, 5.31, \
                  5.36, 5.17, 5.07, 4.97, 5.00, 5.01, 4.85, 4.79, 4.73, 4.76])

    # Calc five future and five past values of the time-series 10th order 
    # autoregressive model

    result1 = time_series_forecast(x, 10, 5)
    result2 = time_series_forecast(x, 10, 5, backcast=True)
    
    
    actual1 = np.array([4.65870, 4.58380, 4.50030, 4.48828, 4.46971])
    print actual1
    print result1
    print result1 - actual1
    print ''
    
    actual2 = np.array([6.94862, 6.91103, 6.86297, 6.77826, 6.70282])
    print actual2
    print result2
    print result2 - actual2


    # Test Coeffs - n-element vector of time-series 
    x = np.array([6.63, 6.59, 6.46, 6.49, 6.45, 6.41, 6.38, 6.26, 6.09, 5.99, \
                  5.92, 5.93, 5.83, 5.82, 5.95, 5.91, 5.81, 5.64, 5.51, 5.31, \
                  5.36, 5.17, 5.07, 4.97, 5.00, 5.01, 4.85, 4.79, 4.73, 4.76])

    # calc coefficients of 5th order auto-regressive model
    result = time_series_coef(x, 5)
    
    # result is
    actual = [1.30168, -0.111783, -0.224527, 0.267629, -0.233363]

    print actual
    print result
    print result - actual

