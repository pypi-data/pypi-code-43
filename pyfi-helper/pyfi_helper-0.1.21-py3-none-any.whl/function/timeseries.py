import datetime as dt
import numpy as np
import pandas as pd
import scipy.signal as sg

"""
本模块主要是常见的宏观序列的处理函数
当前的主要功能是：
1. 获取定基指数
2. 1,2月数据进行处理
3. 将累计值转换为单月值
"""


def yoy2fixedbaseindex(orgfbi, yoylist, option1='index', option2='yoy', fbiloc='start'):
    """
    将同比序列转换为定基指数
    author: HuPeiran
    # input: orgfib, yoylist = pandas.data dataframe
    # option1 = 'index' OR 'mom', option2 = 'yoy' OR 'cumyoy', fbiloc = 'start' OR ?

    # option1 代表初始定基指数的形式，指数形式 - 'index'，环比形式 - 'mom'
    # option2 代表计算定基指数的数据形式，同比数据 - 'yoy'，累计同比数据 - 'cumyoy'
    # option3 用于指定初始定基指数和后面环比数据位置

    # 初始定基指数不能与同比数据叠加
    # 举例：初始定基指数'2011-01:2011-12'，同比数据'2012-01:2018-05'
    # 函数最后将初始定基指数和同比数据一并返回
    :param orgfbi:
    :param yoylist:
    :param option1:
    :param option2:
    :param fbiloc:
    :return:
    """
    startmonth = orgfbi.index[0].month
    endmonth = orgfbi.index[-1].month
    cyc = endmonth - startmonth + 1

    if option1 == 'mom':
        temp = [1 + i for i in orgfbi.iloc[:, 0].values]
        temp[0] = 1
        orgfbi_list = np.cumprod(temp)
        orgfbi_list = [i * 100 for i in orgfbi_list]
    elif option1 == 'index':
        start = orgfbi.iloc[:, 0].values[0]
        temp = [i / start * 100 for i in orgfbi.iloc[:, 0].values]
        orgfbi_list = temp

    startyear = yoylist.iloc[:, 0].index[0].year
    alldatelist = yoylist.index
    allyearlist = [i.year for i in alldatelist]
    temp = list()
    [temp.append(i) for i in allyearlist if not i in temp]  # 取yoy数据的所有年份
    allyearlist = temp

    len_ = len(yoylist[str(allyearlist[-1])])
    if len_ != cyc:
        newdate = pd.date_range(start=dt.date(allyearlist[0], startmonth, 1),
                                end=dt.date(allyearlist[-1], endmonth, 31), freq='M')
        adddata = [0] * (cyc * (len(allyearlist) - 1) + len_) + [np.nan] * (cyc - len_)
        adddata_dataf = pd.DataFrame(data=adddata, index=newdate, columns=['temp'])
        yoylist.columns = ['temp']
        yoylist_new = yoylist + adddata_dataf

    yoy_1year = list()
    yoy_1year.append(orgfbi_list)

    for year_count in allyearlist:
        yoy_1year.append(
            [float(i) / 100 + 1 for i in yoylist_new.loc[str(year_count), :].values])  # dataframe.values = array

    yoy_1year_array = np.array([i for i in yoy_1year])
    re = list(np.cumprod(yoy_1year_array.T, axis=1).T.reshape((1, cyc * (len(allyearlist) + 1)))[0])
    re[-(cyc - len_):] = []
    re = pd.DataFrame(data=re, index=list(orgfbi.index) + list(yoylist.index), columns=['FixedBaseIndex'])
    return re


def macro_adjust(yoy, cyoy, method=1):
    """
    author: Wang Luzhou
    update date: 2018-08-01
    introduction: 去除1月，2月信息用累计同比
    :param yoy:
    :param cyoy:
    :param method: 1:remove Jan data; 2: copy Dec data to Jan
    :return:

    """
    for i in range(len(yoy)):
        if yoy.index[i].month == 2:  # 2月份
            yoy[i] = cyoy[i]
        if yoy.index[i].month == 1:  # 1月份
            if method == 1 or i == 0:
                yoy.iloc[i] = np.nan
            elif method == 2:
                yoy.iloc[i] = yoy.iloc[i - 1]
    return yoy.dropna()


def ffill_mon_data(data):
    """
    author: Wang Luzhou
    update: 2018-08-14
    将数据进行月度级别的填充，并向前复制覆盖na值
    日度数据也可以转换为月度数据
    :param data:
    :return:

    Examples
    --------
    当我们调用人民币定存利率的时候，我们收到的是不规则的低频数据，
    因此需要依靠这个函数将数据转换为月度数据
    """
    return data.resample("M").last().ffill().dropna()


def get_supseason_ind(data):
    """
    输入的为环比数据,返回的是超季节性指数
     # input: data = pandas.series
    :return:
    """
    from pyfi import spring_month
    # 环比数据
    data = data
    # cpi_r = w.edb(codes=[code], begin_date=datetime(1995, 1, 1), end_date=cur_date).iloc[:, 0]
    # 标记春节， 该月有春节则标记True,否则标记False
    spring = pd.Series(index=data.index)
    for i in range(len(data)):
        if data.index[i].month == 1 or i == 0:
            spring_m = spring_month(data.index[i].year)
        if data.index[i].month == spring_m:
            spring[i] = True
        else:
            spring[i] = False
    # 标记完成
    supseason_ind = pd.Series(index=data.index)
    supseason_cum_ind = pd.Series(index=data.index)
    cpi_cum_r = pd.Series(index=data.index)
    window = 5  # 和过去五年作比较
    for i in range(12, len(data)):
        if cpi_cum_r.index[i].month == 1:
            cpi_cum_r[i] = data[i] / 100.0
        else:
            cpi_cum_r[i] = (1 + (0 if np.isnan(cpi_cum_r[i - 1]) else cpi_cum_r[i - 1])) * (1 + data[i] / 100.0) - 1
        past = data[:i]
        past_cum = cpi_cum_r[:i]
        past_spring = spring[:i]
        spring_cur = spring[i]
        chosen = past.loc[(past.index.month == data.index[i].month) & (past_spring == spring_cur)][-window:]
        chosen_cum = past_cum.loc[(past_cum.index.month == cpi_cum_r.index[i].month)][-window:].dropna()
        if len(chosen) > 0:
            avg = chosen.mean()
            supseason_ind[i] = data[i] - avg
        if len(chosen_cum) > 0:
            avg_cum = chosen_cum.mean()
            supseason_cum_ind[i] = cpi_cum_r[i] - avg_cum
    return supseason_ind, supseason_cum_ind


def mean_Jan_Feb(ts):
    """Jan&Feb data Adjustment
    将一个序列的1,2月份的数据进行平均处理
    1,2月的数据都取1,2月数据的均值
    """
    # 输入的时间序列中1月和2月数据必须成对出现！
    ts_ave12 = ts.copy()
    Jan = pd.date_range(ts.index[0], ts.index[-1], freq='A-JAN')
    Feb = pd.date_range(ts.index[0], ts.index[-1], freq='A-FEB')
    ave12 = (ts.loc[Jan].values + ts.loc[Feb].values) / 2  # 将1,2月的数据进行修正
    ts_ave12.loc[Jan] = ave12
    ts_ave12.loc[Feb] = ave12
    ts_ave12.name = 'mean_Jan_Feb'

    return ts_ave12


def get_idx(yoyr, yoycr, base, base_year=2011):
    """
    输入同比和累计同比数据，并制定记住年，获取定基指数
    输入为当月同比，累计同比，基值，基年（默认2015年）,因为CPI和IP的wind提供的定基指数的时长都不长，
    因此综合考虑，我们觉得放在2015年是比较合适的。
    :param yoyr: 当月同比数据
    :param yoycr: 累计同比数据
    :param base: 原始定基指数
    :param base_year: 定基年，默认2015
    :return:
    """
    # 初始化
    date_index = pd.date_range(pd.to_datetime('1990-01-31'), yoycr.index[-1], freq='M')
    idx = pd.DataFrame(index=date_index)
    Sec_Names = yoycr.columns

    for sec_name in Sec_Names:  # 将基年总工业增加值序列（12个月）设为各行业工业增加值的基准
        idx.loc[str(base_year), sec_name] = base[str(base_year)] / base[str(base_year)].iloc[0] * 100

    # 推算基年之后数据
    year = base_year + 1
    while pd.to_datetime(str(year) + '-01-31') <= yoycr.index[-1]:
        year_idx = yoycr[str(year)].index
        last_year_idx = year_idx - pd.tseries.offsets.MonthEnd() * 12
        idx.loc[year_idx] = idx.loc[last_year_idx].values * yoyr.loc[year_idx].values
        idx.loc[year_idx[1]] = idx.loc[last_year_idx[1]].values * yoycr.loc[year_idx[1]].values
        idx.loc[year_idx[0]] = idx.loc[year_idx[1]]  # 1月等于2月
        year = year + 1

    # 推算基年之前数据
    year = base_year
    while pd.to_datetime(str(year) + '-12-31') >= yoycr.index[0]:
        next_year_idx = yoycr[str(year)].index
        year_idx = next_year_idx - pd.tseries.offsets.MonthEnd() * 12
        idx.loc[year_idx] = idx.loc[next_year_idx].values / yoyr.loc[next_year_idx].values
        if pd.to_datetime(str(year - 1) + '-01-31') == year_idx[0]:  # 去年的一月份
            # 2月份的数据用累计同比倒推，并使得1月等于2月
            idx.loc[year_idx[1]] = idx.loc[next_year_idx[1]].values / yoycr.loc[next_year_idx[1]].values
            idx.loc[year_idx[0]] = idx.loc[year_idx[1]]  # 1月等于2月
        year = year - 1

    return idx


def cum2single(series, missingJan=False, pctChange=False):
    """
    将累计值转为单月值 input: pd.series/dataframe
    # 若1月数据缺失 missingJan = True
    # 函数默认返回当月值 要返回环比 pctChange = True
    :param series:
    :param missingJan:
    :param pctChange:
    :return:
    """
    monthindex = pd.date_range(start=series.index[0], end=series.index[-1], freq='A-JAN')
    if missingJan:
        monthindex = pd.date_range(start=series.index[0], end=series.index[-1], freq='A-FEB')
    new_series = series.diff()
    new_series.loc[monthindex] = series.loc[monthindex]
    if pctChange:
        lenzero = len(new_series.loc[new_series.iloc[:, 0] == 0])
        print('caution: number of zeros in series: {0!s}, which may lead NaN or Inf'.format(lenzero))
        new_series = new_series.pct_change()
    return new_series


"""
#-#-#-#-#-#-#-#-#-#-#-#-#-#-季节性调整-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

所有输入应当是月频时间序列，即以月频datetime为index的pandas.Series
需要下载的模组：numpy，pandas，scipy
关于季节性调整的资料参考以下网址：
http://cn.mathworks.com/help/econ/seasonal-adjustment-using-snxd7m-seasonal-filters.html

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#--#-#-#-#-#-
"""


# -#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-滤波函数#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def mean_Jan_Feb(ts):
    """
    平均1、2月数据
    输入的时间序列中1月和2月数据必须成对出现！
    :param ts:
    :return:
    """
    ts_ave12 = ts.copy()
    Jan = pd.date_range(ts.index[0], ts.index[-1], freq='A-JAN')
    Feb = pd.date_range(ts.index[0], ts.index[-1], freq='A-FEB')
    ave12 = (ts.loc[Jan].values + ts.loc[Feb].values) / 2
    ts_ave12.loc[Jan] = ave12
    ts_ave12.loc[Feb] = ave12
    ts_ave12.name = 'mean_Jan_Feb'

    return ts_ave12


def MA13(ts):  # 13-Term Moving Average

    # Symmetric weights for 13-Term MA
    sw13 = np.zeros(13) + 1 / 12
    sw13[0] = 1 / 24
    sw13[-1] = 1 / 24

    arr_ts_MA13 = sg.convolve(ts, sw13, 'same')  # 卷积
    # the following two lines deals with data at end of Series
    arr_ts_MA13[0:6] = arr_ts_MA13[6]
    arr_ts_MA13[-6:] = arr_ts_MA13[-7]
    ts_MA13 = pd.Series(arr_ts_MA13, index=ts.index)
    ts_MA13.name = '13-Term Moving Average'

    return ts_MA13


def MA13C(ts):
    """
    13-Term Moving Average for centering data
    :param ts:
    :return:
    """
    # Symmetric weights for 13-Term MA
    sw13 = np.zeros(13) + 1 / 12
    sw13[0] = 1 / 24
    sw13[-1] = 1 / 24

    arr_ts_MA13C = sg.convolve(ts, sw13, 'same')
    # the following two lines deals with data at end of Series
    # different from original MA13
    arr_ts_MA13C[0:6] = arr_ts_MA13C[12:18]
    arr_ts_MA13C[-6:] = arr_ts_MA13C[-18:-12]
    ts_MA13C = pd.Series(arr_ts_MA13C, index=ts.index)
    ts_MA13C.name = '13-Term Moving Average C'

    return ts_MA13C


def H13(ts):  # 13-Term Henderson filter

    # Henderson filter weights
    swh = np.array([-0.019, -0.028, 0, .066, .147, .214,
                    .24, .214, .147, .066, 0, -0.028, -0.019])
    # Asymmetric weights for end of series
    awh = np.array([[-.034, -.017, .045, .148, .279, .421],
                    [-.005, .051, .130, .215, .292, .353],
                    [.061, .135, .201, .241, .254, .244],
                    [.144, .205, .230, .216, .174, .120],
                    [.211, .233, .208, .149, .080, .012],
                    [.238, .210, .144, .068, .002, -.058],
                    [.213, .146, .066, .003, -.039, -.092],
                    [.147, .066, .004, -.025, -.042, 0],
                    [.066, .003, -.020, -.016, 0, 0],
                    [.001, -.022, -.008, 0, 0, 0],
                    [-.026, -.011, 0, 0, 0, 0],
                    [-.016, 0, 0, 0, 0, 0]])

    # Apply 13-term Henderson filter
    arr_h13 = sg.convolve(ts, swh, 'same')
    arr_h13[-6:] = sg.convolve(ts[-12:].values[:, None], awh, 'valid')
    arr_h13[0:6] = sg.convolve(ts[0:12].values[:, None], np.rot90(awh, 2), 'valid')
    h13 = pd.Series(arr_h13, index=ts.index)
    h13.name = '13-Term Henderson Filter'

    return h13


def S33(ts):  # S3x3 seasonal components

    T = len(ts)
    sidx = []
    for i in range(12):
        sidx.append(np.arange(i, T, 12))

    # Symmetric weights
    sw3 = np.array([1 / 9, 2 / 9, 1 / 3, 2 / 9, 1 / 9])
    # Asymmetric weights for end of series
    aw3 = np.array([[.259, .407], [.37, .407], [.259, .185], [.111, 0]])
    aw3R = [[0, .111], [.185, .259], [.407, .37], [.407, .259]]
    # Apply filter to each month
    shat3 = ts.copy()
    for i in range(12):
        ns = len(sidx[i])
        dat = ts[sidx[i]].copy()
        sd = sg.convolve(dat.values, sw3, 'same')
        sd[0:2] = sg.convolve(dat[0:4].values[:, None], np.rot90(aw3, 2), 'valid')
        sd[-2:] = sg.convolve(dat[-4:].values[:, None], aw3, 'valid')
        shat3.iloc[sidx[i]] = sd

    # 13-term moving average of filtered series
    sb = MA13C(shat3)
    # Center to get final estimate
    s33 = shat3 / sb
    s33.name = 'Seasonal component estimates'

    return s33


def S35(ts):  # S3x5 seasonal Components

    T = len(ts)
    sidx = []
    for i in range(12):
        sidx.append(np.arange(i, T, 12))

    # Symmetric weights
    sw5 = np.zeros(7) + 1 / 5
    sw5[0:2] = [1 / 15, 2 / 15]
    sw5[-2:] = [2 / 15, 1 / 15]
    # Asymmetric weights for end of series
    aw5 = np.array([[.150, .250, .293],
                    [.217, .250, .283],
                    [.217, .250, .283],
                    [.217, .183, .150],
                    [.133, .067, 0],
                    [.067, 0, 0]])
    # Apply filter to each month
    shat5 = ts.copy()
    for i in range(12):
        ns = len(sidx[i])
        dat = ts[sidx[i]].copy()
        sd = sg.convolve(dat.values, sw5, 'same')
        sd[0:3] = sg.convolve(dat[0:6].values[:, None], np.rot90(aw5, 2), 'valid')
        sd[-3:] = sg.convolve(dat[-6:].values[:, None], aw5, 'valid')
        shat5.iloc[sidx[i]] = sd

    # 13-term moving average of filtered series
    sb = MA13C(shat5)
    # Center to get final estimate
    s35 = shat5 / sb
    s35.name = 'Seasonal component estimates'

    return s35


# -#-#-#-#-#-#-#-derive deseasonalized series-#-#-#-#-#-#-#-

def Deseason(ts, Jan_Feb=False):
    """
    # -----是否平均1、2月数据-----
    :param ts:
    :param Jan_Feb:
    :return:
    """
    if Jan_Feb:  # 如果选择平均，则对1,2月数据进行取平均，否则就不做处理
        IVA_av12 = mean_Jan_Feb(ts)
    else:
        IVA_av12 = ts

    # -----Detrend the data using a 13-term moving average-----
    IVA_MA13 = MA13(IVA_av12)
    IVA_xt = IVA_av12 / IVA_MA13

    # -----Apply an S(3,3) seasonal filter to deseasonalize-----
    IVA_S33 = S33(IVA_xt)
    IVA_DeSeason = IVA_av12 / IVA_S33  # Deseasonalize series

    # -----Apply a 13-term Henderson filter to improve detrending-----
    IVA_H13 = H13(IVA_DeSeason)
    IVA_xt2 = IVA_av12 / IVA_H13  # New detrended series

    # -----Apply an S(3,5) seasonal filter to improve deseasonalizing-----
    IVA_S35 = S35(IVA_xt2)
    IVA_DeSeason2 = IVA_av12 / IVA_S35
    IVA_DeSeason2.name = 'Deseasonalized IVA'

    return IVA_DeSeason2

################### X13 ########################
