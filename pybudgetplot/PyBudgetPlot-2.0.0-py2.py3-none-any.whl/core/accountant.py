import pandas as pd

from pbp.core import calendar
from pbp.core.budget import Budget


def calculate_data(budget: Budget) -> pd.DataFrame:
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
