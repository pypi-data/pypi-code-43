from statsmodels.tsa.stattools import adfuller
import pandas as pd
import matplotlib.pyplot as plt


def test_stationarity(timeseries):
    from statsmodels.tsa.stattools import adfuller

    # 决定起伏统计
    rolmean = timeseries.rolling(window=12).mean()  # 对size个数据进行移动平均
    #     rol_weighted_mean = pd.ewma(timeseries, span=12)
    rol_weighted_mean = timeseries.ewm(span=12).mean()  # 对size个数据进行加权移动平均
    rolstd = timeseries.rolling(window=12).std()  # 偏离原始值多少
    # 画出起伏统计
    orig = plt.plot(timeseries, color='blue', label='Original')
    mean = plt.plot(rolmean, color='red', label='Rolling Mean')
    weighted_mean = plt.plot(rol_weighted_mean, color='green', label='weighted Mean')
    std = plt.plot(rolstd, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)
    # 进行df测试
    print('Result of Dickry-Fuller test')
    dftest = adfuller(timeseries, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of observations Used'])
    for key, value in dftest[4].items():
        dfoutput['Critical value(%s)' % key] = value
    print(dfoutput)
