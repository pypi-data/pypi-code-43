import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
import numpy as np


class ADF(object):
    def __init__(self):
        self.p_value = None
        self.five_perc_stat = None
        self.perc_stat = None
        self.p_min = .0
        self.p_max = .05
        self.look_back = 63

    def apply_adf(self, time_series):
        model = ts.adfuller(time_series, 1)
        self.p_value = model[1]
        self.five_perc_stat = model[4]['5%']
        self.perc_stat = model[0]

    def use_P(self):
        return (self.p_value > self.p_min) and (self.p_value < self.p_max)

    def use_critical(self):
        return abs(self.perc_stat) > abs(self.five_perc_stat)


class Half_Life(object):
    def __init__(self):
        self.hl_min = 1.0
        self.hl_max = 42.0
        self.look_back = 43
        self.half_life = None

    def apply_half_life(self, time_series):
        lag = np.roll(time_series, 1)
        lag[0] = 0
        ret = time_series - lag
        ret[0] = 0

        # adds intercept terms to X variable for regression
        lag2 = sm.add_constant(lag)

        model = sm.OLS(ret, lag2)
        res = model.fit()

        self.half_life = -np.log(2) / res.params[1]

    def use(self):
        return (self.half_life < self.hl_max) and (self.half_life > self.hl_min)


class Hurst(object):
    def __init__(self):
        self.h_min = 0.0
        self.h_max = 0.4
        self.look_back = 126
        self.lag_max = 100
        self.h_value = None

    def apply_hurst(self, time_series):
        """Returns the Hurst Exponent of the time series vector ts"""
        # Create the range of lag values
        lags = range(2, self.lag_max)

        # Calculate the array of the variances of the lagged differences
        tau = [np.sqrt(np.std(np.subtract(time_series[lag:], time_series[:-lag]))) for lag in lags]

        # Use a linear fit to estimate the Hurst Exponent
        poly = np.polyfit(np.log10(lags), np.log10(tau), 1)

        # Return the Hurst exponent from the polyfit output
        self.h_value = poly[0] * 2.0

    def use(self):
        return (self.h_value < self.h_max) and (self.h_value > self.h_min)


