# 考虑到底是输入净值曲线还是输入每日涨跌幅
# 最大回撤
maxdd = lambda eqd: (eqd.cumsum().expanding().max() - eqd.cumsum()).max()



# 月度夏普比率
def m_sharpe(eqd, bk=0.0):
    """monthly sharpe ratio"""
    try:
        if eqd.sum() == 0:
            return -100
        return ((eqd.mean() - bk / 12) / eqd.std()) * (12 ** 0.5)
    except BaseException as e:
        print(e)

# 超额夏普比率
def excess_msp(eqd, base_eqd, bk=0.0):
    return m_sharpe(eqd, bk) - m_sharpe(base_eqd, bk)