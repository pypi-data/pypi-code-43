import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from pbp import time_util
from pbp.datamodel import Budget

register_matplotlib_converters()


def _build_data(budget: Budget, start=None, end=None):
    start = start or time_util.get_today()
    end = end or time_util.get_next_year()

    data = pd.DataFrame(
        index=pd.date_range(start=start, end=end)
    )

    for item in budget:
        dates = time_util.get_dates(item.frequency, start, end)
        item_data = pd.DataFrame(
            data={item.description: item.amount},
            index=pd.DatetimeIndex(pd.Series(dates))
        )
        data = pd.concat([data, item_data], axis=1).fillna(0)

    data["total"] = data.sum(axis=1)
    data["cum_total"] = data["total"].cumsum()

    return data


def _plot_data(data):
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.total, label="Daily Total")
    plt.plot(data.index, data.cum_total, label="Cumulative Total")
    plt.legend()
    plt.show()


def plot_budget(budget: Budget, start=None, end=None):
    data = _build_data(budget, start, end)
    _plot_data(data)
