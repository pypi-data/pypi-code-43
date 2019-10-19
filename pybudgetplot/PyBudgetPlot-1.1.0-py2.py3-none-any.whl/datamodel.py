import logging
from collections import Sequence
from io import StringIO
from pathlib import Path
from typing import Tuple, List

import yaml
from tabulate import tabulate

from pbp.core import calendar

_log = logging.getLogger(__file__)


class BudgetItem:
    description: str
    amount: int
    frequency: str

    def __init__(self, description, amount, frequency):
        self.description = description or ""
        self.amount = int(amount) if amount else 0
        self.frequency = frequency or ""

    def __eq__(self, other):
        if isinstance(other, BudgetItem):
            return (self.description == other.description
                    and self.amount == other.amount
                    and self.frequency == other.frequency)
        return False

    def __repr__(self):
        return f"BudgetItem('{self.description}', {self.amount}, '{self.frequency}')"

    def as_tuple(self) -> Tuple[str, int, str]:
        return self.description, self.amount, self.frequency

    def get_dates(self, start=None, end=None) -> List[str]:
        return [calendar.format_date(date)
                for date
                in calendar.get_dates(self.frequency, start, end)]


class Budget(Sequence):

    def __init__(self):
        self.start_date = calendar.get_today()
        self.end_date = calendar.get_next_year()
        self._items: List[BudgetItem] = []

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __repr__(self):
        return f"Budget({self._items})"

    def __str__(self):
        return self.as_table()

    def __eq__(self, other):
        if isinstance(other, Budget):
            return self._items == other._items
        return False

    def add_item(self, description, amount, frequency) -> BudgetItem:
        item = BudgetItem(description, amount, frequency)
        self._items.append(item)
        return item

    def as_dict(self):
        data = dict(
            Dates=dict(
                start=calendar.format_date(self.start_date),
                end=calendar.format_date(self.end_date)
            )
        )

        for item in self:
            data[item.description] = dict(amount=item.amount, frequency=item.frequency)
        return data

    def as_table(self, include_dates=False, tablefmt="fancy_grid"):

        headers = ["DESCRIPTION", "AMOUNT", "FREQUENCY"]
        if include_dates:
            headers.append("DATES")

        details = []
        for item in self:
            if include_dates:
                dates = item.get_dates(self.start_date, self.end_date)
                dates_text = ", ".join(dates[:5]) + f" ... ({len(dates)} dates)"
                details.append(item.as_tuple() + (dates_text,))
            else:
                details.append(item.as_tuple())

        period_start = calendar.format_date(self.start_date)
        period_end = calendar.format_date(self.end_date)
        return f"Budget(start={period_start}, end={period_end})\n" + tabulate(
            tabular_data=details,
            headers=headers,
            stralign="left",
            floatfmt=".2f",
            tablefmt=tablefmt
        )

    @classmethod
    def load(cls, file):
        return cls.from_yaml(Path(file).read_text(encoding="utf-8"))

    def save(self, file):
        Path(file).write_text(self.to_yaml(), encoding="utf-8")

    @classmethod
    def from_yaml(cls, text: str):
        budget = cls()

        budget_definition = yaml.load(StringIO(text), Loader=yaml.SafeLoader)

        date_range = budget_definition.pop("Dates", None)
        if date_range:
            budget.start_date = calendar.get_dates(date_range.get("start"))[0]
            budget.end_date = calendar.get_dates(date_range.get("end"))[0]

        for description, details in budget_definition.items():
            budget.add_item(description, details.get("amount"), details.get("frequency"))

        return budget

    def to_yaml(self) -> str:
        buffer = StringIO()
        yaml.dump(self.as_dict(), buffer, Dumper=yaml.SafeDumper, sort_keys=False)
        return buffer.getvalue()
