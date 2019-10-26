import statsmodels.api as sm
from scipy.odr import *
import pandas as pd
import numpy as np
from pykalman import KalmanFilter
from data.source import data
from SETTINGS import K_ARR
from datetime import datetime

class SpreadBuilder():
    def __init__(self, window=365, from_="2015-01-01", to_=datetime.now().strftime("%Y-%m-%d")):
        self.window = window
        self.from_ = from_
        self.to_ = to_

    @staticmethod
    def _diff(y, x):
        spread = y - x
        return spread

    @staticmethod
    def _ratio(y, x):
        spread = y / x
        return spread

    @staticmethod
    def _zscore(y, x, window):
        """
        Ratio Moving Average Differential Method
        """
        ratio = y / x
        rolling_ratio = ratio.rolling(window='{}D'.format(window), min_periods=int(window / 2))
        ratio_ma = rolling_ratio.mean()
        ratio_std = rolling_ratio.std()

        spread = (ratio - ratio_ma) / ratio_std
        return spread.dropna()

    @staticmethod
    def _ROsMA(y, x):
        """
        Ratio Moving Average Differential Method
        """
        ratio = y / x
        ratio_ma = ratio.mean()

        spread = (ratio / ratio_ma - 1) * 100
        return spread.dropna()

    @staticmethod
    def _DROsMA(y, x, window):
        """
        Ratio Moving Average Differential Method
        """
        ratio = y / x
        rolling_ratio = ratio.rolling(window='{}D'.format(window), min_periods=int(window / 2))
        ratio_ma = rolling_ratio.mean()

        spread = (ratio / ratio_ma - 1) * 100
        return spread.dropna()

    @staticmethod
    def _OLS(y, x):
        """
        Ordinary Least Squares Regression Method
        """
        model = sm.OLS(y, sm.tools.add_constant(x)).fit()

        beta = model.params[1]
        intercept = model.params[0]
        spread = y - x * beta - intercept

        return spread, beta, intercept

    @staticmethod
    def f(B, x):
        """
        For TLS
        """
        return B[0] * x + B[1]

    @staticmethod
    def _TLS(y, x):
        """
        Total Least Squares Regression Method
        """
        sx = np.std(x)
        sy = np.std(y)

        linear = Model(SpreadBuilder.f)
        mydata = RealData(x=x, y=y, sx=sx, sy=sy)
        myodr = ODR(mydata, linear, beta0=[5., 2.])
        myoutput = myodr.run()

        beta, intercept = myoutput.beta

        spread = y - x * beta - intercept
        return spread, beta, intercept

    @staticmethod
    def _NPI(y, x):
        y_norm = (y - y.mean()) / y.std()
        x_norm = (x - x.mean()) / x.std()
        spread = y_norm - x_norm

        return spread, y_norm, x_norm

    @staticmethod
    def _zscore(y, x, window):
        """
        Ratio ZScore
        """
        ratio = y / x
        rolling_ratio = ratio.rolling(window='{}D'.format(window), min_periods=int(window / 2))
        ratio_ma = rolling_ratio.mean()
        ratio_std = rolling_ratio.std()

        spread = (ratio - ratio_ma) / ratio_std
        return spread.dropna()

    @staticmethod
    def _KF(y, x, delta=1e-5):
        delta = delta
        trans_cov = delta / (1 - delta) * np.eye(2)

        obs_mat = np.vstack(
            [x, np.ones(x.shape)]
        ).T[:, np.newaxis]

        kf = KalmanFilter(
            n_dim_obs=1,
            n_dim_state=2,
            initial_state_mean=np.zeros(2),
            initial_state_covariance=np.ones((2, 2)),
            transition_matrices=np.eye(2),
            observation_matrices=obs_mat,
            observation_covariance=1.0,
            transition_covariance=trans_cov
        )

        state_means, covs = kf.filter(y)

        beta = state_means[:, 0]
        intercept = state_means[:, 1]

        spread = y - x * beta - intercept

        beta = pd.DataFrame(data=beta, index=spread.index, columns=['Beta'])
        intercept = pd.DataFrame(data=intercept, index=spread.index, columns=['Intercept'])

        return spread, beta, intercept

    @staticmethod
    def build(pair, methods, window):
        # Abs Price
        y = pair.data['y']
        x = pair.data['x']

        # Log Price
        pair.data['log_y'] = log_y = np.log(y)
        pair.data['log_x'] = log_x = np.log(x)

        for method in methods:
            if method == 'diff':
                pair.spread[method] = SpreadBuilder._diff(y=y, x=x)

            elif method == 'Ratio':
                # Abs Price
                pair.spread[method] = SpreadBuilder._ratio(y=y, x=x)

            elif method == 'ROsMA':  # Ratio Moving Average Differential
                # Abs Price
                pair.spread[method] = SpreadBuilder._ROsMA(y=y, x=x)

            elif method == 'DROsMA':  # Ratio Moving Average Differential
                # Abs Price
                pair.spread[method] = SpreadBuilder._DROsMA(y=y, x=x, window=window)

            elif method == 'OLS':  # Ordinary Least Squared
                # Log Price
                pair.spread[method], pair.hedge_ratio[method], pair.intercept[method] = SpreadBuilder._OLS(y=log_y,
                                                                                                           x=log_x)

            elif method == 'TLS':  # Total Least Squared
                # Log Price
                pair.spread[method], pair.hedge_ratio[method], pair.intercept[method] = SpreadBuilder._TLS(y=log_y,
                                                                                                           x=log_x)

            elif method == 'NPI':  # Normalized Price Index Differential
                # Abs Price
                pair.spread[method], pair.data[method + '_y'], pair.data[method + '_x'] = SpreadBuilder._NPI(y=y, x=x)

            elif method == 'KF':  # Kalman Filter
                # Log Price
                pair.spread[method], pair.hedge_ratio[method], pair.intercept[method] = SpreadBuilder._KF(y=log_y,
                                                                                                          x=log_x,
                                                                                                          delta=1e-5)
            elif method == 'zscore':
                pair.spread[method] = SpreadBuilder._zscore(y=y,x=x, window=window)
            else:
                print("Incorrect Spread Method : ", method)
                raise Exception


            rolling_spread = pair.spread[method].rolling(window='{}D'.format(window),
                                                         min_periods=int(window / 2))
            rolling_mean = rolling_spread.mean().dropna()
            rolling_std = rolling_spread.std().dropna()
            pair.data[method + '_mean'] = rolling_mean
            pair.data[method + '_std'] = rolling_std

            for k in K_ARR:
                ub_suffix = '_ub_' + str(k)
                lb_suffix = '_lb_' + str(k)
                pair.data[method + ub_suffix] = rolling_mean + k * rolling_std
                pair.data[method + lb_suffix] = rolling_mean - k * rolling_std

        pair.data['rolling_corr'] = y.pct_change().rolling("{}D".format(window)).corr(x.pct_change())
        return pair

    def calculate(self, pair, methods=['Ratio', 'ROsMA', 'TLS', 'KF'], freq='1d'):
        y_asset = pair.y_asset
        x_asset = pair.x_asset

        prices = data.history([y_asset, x_asset], ["CLOSE"], from_date=self.from_, to_date=self.to_, freq=freq)

        paired_prices = pd.concat([prices[y_asset.use()]["CLOSE"], prices[x_asset.use()]["CLOSE"]], axis=1,
                                  join='inner').dropna()
        paired_prices.columns = ['y', 'x']

        # Abs Price
        pair.data['y'] = paired_prices['y']
        pair.data['x'] = paired_prices['x']

        SpreadBuilder.build(pair=pair, methods=methods, window=self.window)
