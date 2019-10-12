import math
import numpy as np
import pandas as pd


class BootstrapYieldCurve(object):
    def __init__(self, ytms=[]):
        self.terms = list(range(1, len(ytms) + 1))
        self.ytms = pd.Series(ytms, index=self.terms)
        self.spot_rates = pd.Series(index=self.terms)
        self.forward_rates = pd.Series(index=self.terms)

    def get_ytms(self):
        """
        获取到期收益率曲线
        :return:
        """
        return self.ytms

    def get_spot_rates(self):
        """
        获取即期收益率曲线
        :return:
        """
        for T in self.terms:
            ytm = self.ytms.loc[T]
            self.spot_rates.loc[T] = self.__calculate_spot_rate__(T, ytm)
        return self.spot_rates

    def get_forward_rates(self, key_terms=[]):
        """
        获取远期收益率曲线
        :return:
        """
        if len(key_terms) == 0:
            # 无期限筛选
            key_terms = self.terms
        self.spot_rates = self.get_spot_rates()
        self.forward_rates = pd.Series(index=key_terms)
        self.forward_rates.iloc[0] = self.spot_rates.iloc[0]
        for i in range(1, len(key_terms)):
            t = key_terms[i]
            t_ahead = key_terms[i - 1]
            self.forward_rates.iloc[i] = 100 * ((((self.spot_rates.loc[t] / 100 + 1) ** t) / (
                        (self.spot_rates.loc[t_ahead] / 100 + 1) ** t_ahead))**(1/(t-t_ahead))-1)
        return self.forward_rates

    def __calculate_spot_rate__(self, T, ytm):
        value = 100
        for i in range(T - 1):
            t = i + 1
            spot_rate = self.spot_rates.iloc[i]
            discounted_coupon = ytm / ((1 + spot_rate / 100) ** t)
            value -= discounted_coupon
        spot_rate = (((ytm + 100) / value) ** (1 / T) - 1) * 100
        return spot_rate


if __name__ == "__main__":
    yield_curve = BootstrapYieldCurve(ytms=[3, 3.3, 3.4, 3.5, 3.6, 3.7])
    y = yield_curve.get_forward_rates()

    import matplotlib.pyplot as plt

    plt.plot(y.index, y.values)
    plt.title("Spot Rate Curve")
    plt.ylabel("Spot Rate (%)")
    plt.xlabel("Spot rates in Years")
    plt.show()
