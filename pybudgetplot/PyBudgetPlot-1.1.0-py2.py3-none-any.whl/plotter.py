import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from pbp.core import calendar
from pbp.core.budget import Budget

register_matplotlib_converters()


def generate_budget_data(budget: Budget) -> pd.DataFrame:
    data = pd.DataFrame(
        index=pd.date_range(start=budget.start_date, end=budget.end_date)
    )

    for item in budget:
        dates = calendar.get_dates(item.frequency, budget.start_date, budget.end_date)
        item_data = pd.DataFrame(
            data={item.description: item.amount},
            index=pd.DatetimeIndex(pd.Series(dates))
        )
        data = pd.concat([data, item_data], axis=1).fillna(0)

    data["total"] = data.sum(axis=1)
    data["cum_total"] = data["total"].cumsum()

    return data


def export_budget(budget: Budget, file):
    generate_budget_data(budget).to_csv(file, index_label="Id", encoding="utf-8")


def plot_budget_data(data):
    plt.figure(figsize=(10, 5))
    plt.plot(data.index, data.total, label="Daily Total")
    plt.plot(data.index, data.cum_total, label="Cumulative Total")
    plt.legend()
    plt.show()


def plot_budget(budget: Budget):
    plot_budget_data(
        generate_budget_data(budget)
    )
