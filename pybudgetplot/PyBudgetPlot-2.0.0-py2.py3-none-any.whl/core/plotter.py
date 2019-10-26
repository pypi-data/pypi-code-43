import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


def plot_data(data: pd.DataFrame):
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.total, label="Daily Total")
    plt.plot(data.index, data.cum_total, label="Cumulative Total")
    plt.legend()
    plt.show()
