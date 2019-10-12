import numpy as np
import pandas as pd
from pyfi import Map


def performance_report1(curve):
    """
    只要输入净值曲线即可
    :param curve:
    :return:
    """
    cum_return = curve / curve[0] - 1
    day_return = curve.pct_change()
    report = Map()
    # cumulative return
    report["cumlative return"] = cum_return[-1]
    # annualized retrun 
    report["annualized return"] = compute_annual_profit(cum_return)
    # annualized volatility
    report["annualized volatility"] = compute_annual_vol(day_return)
    # sharp ratio
    report["sharp ratio"] = sharpe_gen(cum_return)
    # max drawdown
    report["max drawdown"] = maxdd_gen(cum_return)
    # worst monthly return
    report["worst monthly return"] = monthly_rtn(day_return)[1]
    # best monthly return
    report["best monthly return"] = monthly_rtn(day_return)[0]
    # worst yearly return
    report["worst yearly return"] = yearly_rtn(day_return)[1]
    # best yearly return
    report["best yearly return"] = yearly_rtn(day_return)[0]
    return report


def sharpe_gen(cum_return, risk_free_rate=2.45, freq="M"):
    """
    计算年度夏普率
    输入：日度收益序列
    输出：年度夏普率
    """
    rfr = risk_free_rate/100/(245 if freq == "D" else 12)
    return_list = (cum_return + 1).pct_change()
    return np.sqrt((245 if freq == "D" else 12)) * (np.mean(return_list)-rfr) / np.std(return_list)


def maxdd_gen(cum_return):
    """
    计算最大回撤
    输入：累计收益序列
    输出：最大回撤
    """
    new_high = cum_return[0]
    DD = 0
    for idx in range(1, len(cum_return)):
        new_high = max(new_high, cum_return[idx])
        DD_current = new_high - cum_return[idx]
        if DD_current > DD:
            DD = DD_current
    return DD


def return_gen(closex, trade_signal, tran_cost=0):
    """
    计算累计收益、日度收益、交易次数、胜率、夏普率、盈亏比
    输入：
    -closex： 计算收益所需要的价格序列
    -trade_signal: 交易信号，1代表多头，-1代表空头，0代表没有交易信号
    -tran_cost: 交易手续费，5代表万分之五
    输出：
    累计收益序列、日度收益序列、交易次数、夏普率、盈亏比
    """
    cum_return = [0.0]
    day_return1 = [0.0]
    trade_num = 0
    cum_stage = 0.0
    close_init = closex[1]
    cum_return_temp = 0.0
    cum_return_once = 0.0
    win_num = 0
    win = []
    lose = []
    for idx in range(1, len(trade_signal) - 1):
        factor = trade_signal[idx]
        cum_stage = cum_return[-1]
        if factor != 0:
            if trade_signal[idx - 1] != factor or idx == 1:
                close_init = closex[idx]
                ls_signal = factor
            if factor == ls_signal:
                cum_return_temp = cum_stage + (closex[idx + 1] - closex[idx]) / close_init * factor
                cum_return_once = cum_return_once + (closex[idx + 1] - closex[idx]) / close_init * factor
            if factor != trade_signal[idx + 1]:
                cum_return_temp -= tran_cost / float(10000)
                cum_return_once -= tran_cost / float(10000)
                if cum_return_once >= 0:
                    win_num += 1
                    win.append(cum_return_once)
                else:
                    lose.append(cum_return_once)
                trade_num += 1
                cum_return_once = 0
        cum_return.append(cum_return_temp)

    cum_return.append(cum_return[-1])
    day_return = list(np.diff(cum_return[:]))
    day_return = day_return1 + day_return
    sharpe_ratio = sharpe_gen(day_return)
    win_lose = -np.mean(win) / np.mean(lose)
    return cum_return, day_return, trade_num, win_num, sharpe_ratio, win_lose


def compute_annual_profit(cum_return, freq="M"):
    """
    计算年化收益率
    输入：cum_return: 累计收益序列
    输出：年华收益率
    """
    annual_profit = 0
    if len(cum_return) > 0:
        years = len(cum_return) / (245 if freq == "D" else 12)
        annual_profit = pow(cum_return[-1] + 1, 1 / years) - 1
    return annual_profit


def compute_annual_vol(day_return, freq="M"):
    """
    计算年化波动率
    输入：日回报列表序列
    输出：年化波动率
    """
    vol = np.std(day_return) * np.sqrt((245 if freq == "D" else 12))
    return vol


def monthly_rtn(day_return):
    """
    计算最好与最差月度收益率
    输入：day_return:日度收益，为Series格式
    输出：最好月度收益：max_rtn
         最差月度收益：min_rtn
    """
    resample_rtn = day_return.resample('M').sum()
    max_rtn = resample_rtn.max()
    min_rtn = resample_rtn.min()
    return max_rtn, min_rtn


def yearly_rtn(day_return):
    """
    计算最好与最差年度收益率
    输入：day_return:日度收益，为Series格式
    输出：最好年度收益：max_rtn
         最差年度收益：min_rtn
    """
    resample_rtn = day_return.resample('Y').sum()
    max_rtn = resample_rtn.max()
    min_rtn = resample_rtn.min()
    return max_rtn, min_rtn
