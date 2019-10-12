# 常用债券计算函数
from datetime import timedelta, datetime
import scipy.optimize as optimize
import pandas as pd
import numpy as np


def get_ytm_by_net(net, maturity, cupn, freq, par=100, guess=3):
    """
    根据净价, 待偿期限，票息，付息次数，面值计算债券的到期收益率
    :param net:
    :param par:
    :param maturity:
    :param cupn:
    :param freq:
    :param guess:
    :return:
    """
    yearsToNxCupn = maturity - 1. / freq * np.floor(freq * maturity)
    cupnCount = int(np.ceil(freq * maturity))
    coupon = cupn / 100. * par / freq
    if yearsToNxCupn == 0.:
        dt = [(i + 1.) / freq for i in range(cupnCount)]
    else:
        dt = [yearsToNxCupn + i / freq for i in range(cupnCount)]
    ytm_func = lambda y: sum([coupon / (1. + y / 100. / freq) ** (freq * t) for t in dt]) + \
                         par / (1. + y / 100. / freq) ** (freq * maturity) - (
                                 1. / freq - yearsToNxCupn) * cupn - net
    return optimize.newton(ytm_func, guess)


def get_dirty(ytm, maturity, cupn, freq, par=100.):
    """
    based on ytm, maturity, coupon and frequency to calculate the dirty price
    :param ytm:
    :param par:
    :param maturity:
    :param cupn: 3.65 instead of 0.0365
    :param freq:
    :return:
    """
    yearsToNxCupn = maturity - 1.0 / freq * np.floor(freq * maturity)
    cupnCount = int(np.floor(freq * maturity)) + 1
    coupon = cupn / 100. * par / freq
    if yearsToNxCupn == 0:
        dt = [(i + 1.) / freq for i in range(cupnCount)]  # 记录付息时间点
    else:
        dt = [yearsToNxCupn + i / freq for i in range(cupnCount)] # 记录付息时间点
    return sum([coupon / (1. + ytm / 100. / freq) ** (freq * t) for t in dt]) + \
        par / (1. + ytm / 100. / freq) ** (freq * maturity)


def get_net(ytm, par, maturity, cupn, freq):
    daysToNxCupn = maturity - 1.0 / freq * np.floor(freq * maturity)
    dirty = get_dirty(ytm, maturity, cupn, freq, par)
    return dirty - (1. / freq - daysToNxCupn) * cupn


def get_years_to_nxcupn(maturity, freq):
    """
    calculate the period to next coupon marked by year unit
    :param maturity:
    :param freq:
    :return:
    """
    yearsToNxCupn = maturity - 1.0 / freq * np.floor(freq * maturity)
    return yearsToNxCupn

