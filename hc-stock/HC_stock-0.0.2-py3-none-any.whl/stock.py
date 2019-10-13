import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt

class stock():
    @staticmethod
    def plot(ls, start = '2019-09-01', end = '2019-10-12', price = 'close'):
        isList = False
        if isinstance(ls, str):
            data = ts.get_hist_data(ls,start = start, end = end)[price]
            data.sort_index(ascending = True, inplace = True)
            plt.plot(data, label = ls)
        elif isinstance(ls, list):
            data = {}
            for i,s in enumerate(ls):
                data[i] = ts.get_hist_data(s,start = start, end = end)[price]
                data[i].sort_index(ascending = True, inplace = True)
                plt.plot(data[i], label = s)