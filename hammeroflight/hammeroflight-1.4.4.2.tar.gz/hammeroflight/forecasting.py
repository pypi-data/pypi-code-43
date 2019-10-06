import numpy as np

def plot_forecast(true, pred):

    '''
    Author: Aru Raghuvanshi

    This function plots the graph of the Truth values
    and Predicted values of a predictive model and
    visualizes in the same frame. The truth values
    and pred value sizes should be same and both
    should be sharing the same x-axis.


    Arguments: truth value, predicted value
    Returns: Plot

    '''

    plt.figure(figsize=(15, 6))
    plt.plot(true, color='b', label='Test')
    plt.plot(pred, color=np.random.rand(3,), label='Predicted')
    plt.xlabel('Variable', fontsize=16)
    plt.ylabel('Target', fontsize=16)
    plt.title('Truth v/s Prediction Chart', fontsize=16)
    plt.legend()
    plt.show()


# ======================== ORDERTUNER ========================= ]


def arima_ordertuner(lower_range, upper_range):

    '''
    Author: Aru Raghuvanshi

    This function automatically tunes the p, d, q
    values for minimum AIC score and displays the
    (p, d, q) values as a tuple which can be used
    to tune the ARIMA model.

    Arguments: lower_range, upper_range
    Returns: Best Parameters for ARIMA Model

    Ex: result = tune_order(0,5)
    Will return best permutations for Order of
    p,d,q with values of each of p d and q between
    0 and 5.

    '''

    import itertools
    p = d = q = range(lower_range, upper_range)
    pdq = list(itertools.product(p, d, q))

    aiclist = []
    paramlist = []

    for param in pdq:
        try:
            arima = ARIMA(train, order=param)
            arima_fit = arima.fit()
            print(param, arima_fit.aic)  # AIC = Akaike
            aiclist.append(arima_fit.aic)
            paramlist.append(param)
        except:
            print('Exception Overruled')
            continue

    m = min(aiclist)
    ind = aiclist.index(m)
    paramno = paramlist[ind]
    print(f'Best Parameter: {paramno}, Min AIC Value: {m}')

    return paramno, m

# ================================================================================ ]