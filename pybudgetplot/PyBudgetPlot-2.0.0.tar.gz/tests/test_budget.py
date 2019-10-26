import collections
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch, call

import pandas as pd

from pbp.core.budget import BudgetItem, Budget
from pbp.core.calendar import get_today, get_next_year, format_date

PERIOD_START = format_date(get_today())

PERIOD_END = format_date(get_next_year())

BUDGET_YAML_CONTENTS = f"""Dates:
  start: '{PERIOD_START}'
  end: '{PERIOD_END}'
Salary:
  amount: 1000
  frequency: Every month starting on 5th November
Rent:
  amount: -500
  frequency: Every month starting on 20th November
"""

BUDGET_TABLE = f"""
Budget(start={PERIOD_START}, end={PERIOD_END})
╒═══════════════╤══════════╤═══════════════════════════════════╕
│ DESCRIPTION   │   AMOUNT │ FREQUENCY                         │
╞═══════════════╪══════════╪═══════════════════════════════════╡
│ Salary        │     1000 │ every month starting on June 5th  │
├───────────────┼──────────┼───────────────────────────────────┤
│ Rent          │     -500 │ every month starting on June 20th │
╘═══════════════╧══════════╧═══════════════════════════════════╛
""".strip()


class BudgetItemTest(TestCase):

    def test_creation(self):
        description = "item desc"
        amount = 123
        frequency = "every Friday"
        item = BudgetItem(description, amount, frequency)

        self.assertEqual(description, item.description)
        self.assertEqual(amount, item.amount)
        self.assertEqual(frequency, item.frequency)
        self.assertIsInstance(item.amount, int)

    def test_as_tuple(self):
        description = "item desc"
        amount = 123
        frequency = "every Friday"
        item = BudgetItem(description, amount, frequency)

        expected_tuple = description, 123.0, frequency
        actual_tuple = item.as_tuple()

        self.assertEqual(expected_tuple, actual_tuple)

    def test_repr(self):
        description = "item desc"
        amount = 123
        frequency = "every Friday"
        item = BudgetItem(description, amount, frequency)
        expected_text = "BudgetItem('item desc', 123, 'every Friday')"
        actual_text = repr(item)
        self.assertEqual(expected_text, actual_text)

    def test_get_dates_calls_time_util(self):
        frequency = "every week"
        item = BudgetItem("expense", 23.4, frequency)

        with patch("pbp.core.calendar.get_dates", autospec=True) as mock_get_dates:
            mock_get_dates.return_value = []
            item.get_dates()
            self.assertListEqual([call(frequency, None, None)], mock_get_dates.mock_calls)

        start = object()
        end = object()
        with patch("pbp.core.calendar.get_dates", autospec=True) as mock_get_dates:
            mock_get_dates.return_value = []
            item.get_dates(start, end)
            self.assertListEqual([call(frequency, start, end)], mock_get_dates.mock_calls)

    def test_get_dates_formats_dates(self):
        item = BudgetItem("expense", 23.4, "irrelevant")

        date = pd.Timestamp("2019-10-29")
        date_str = format(date, "%Y-%m-%d")
        expected_dates = [date_str, date_str]

        with patch("pbp.core.calendar.get_dates", autospec=True) as mock_get_dates:
            mock_get_dates.return_value = [date, date]
            actual_dates = item.get_dates()

        self.assertListEqual(expected_dates, actual_dates)


class BudgetTest(TestCase):

    def test_instance_creation(self):
        budget = Budget()

        self.assertEqual(budget.start_date, get_today())
        self.assertEqual(budget.end_date, get_next_year())

        self.assertIsInstance(budget, collections.Iterable)
        self.assertIsInstance(budget, collections.Sequence)
        self.assertIsInstance(budget, collections.Container)
        self.assertIsInstance(budget, collections.Sized)
        self.assertEqual(0, len(budget))

    def test_add_item_changes_size(self):
        budget = Budget()

        salary = budget.add_item("Salary", 1000, "every month starting on June 5th")
        self.assertEqual(1, len(budget))
        self.assertTrue(salary in budget)

        rent = budget.add_item("Rent", -500, "every month starting on June 20th")
        self.assertEqual(2, len(budget))
        self.assertTrue(rent in budget)

    def test_repr(self):
        budget = Budget()
        budget.add_item("Salary", 1000, "every month starting on June 5th")
        expected_repr = "Budget([BudgetItem('Salary', 1000, 'every month starting on June 5th')])"
        self.assertEqual(expected_repr, repr(budget))

        budget.add_item("Rent", -500, "every month starting on June 20th")
        expected_repr = "Budget([BudgetItem('Salary', 1000, 'every month starting on June 5th'), BudgetItem('Rent', -500, 'every month starting on June 20th')])"
        self.assertEqual(expected_repr, repr(budget))

    def test_str(self):
        budget = Budget()
        budget.add_item("Salary", 1000, "every month starting on June 5th")
        budget.add_item("Rent", -500, "every month starting on June 20th")

        self.assertEqual(BUDGET_TABLE, str(budget))

    def test_from_to_yaml(self):
        salary = BudgetItem("Salary", 1000, "Every month starting on 5th November")
        rent = BudgetItem("Rent", -500, "Every month starting on 20th November")

        initial_budget = Budget.from_yaml(BUDGET_YAML_CONTENTS)
        self.assertIn(salary, initial_budget)
        self.assertIn(rent, initial_budget)
        self.assertListEqual([salary, rent], list(initial_budget))

        generated_yaml = initial_budget.to_yaml()

        reloaded_budget = Budget.from_yaml(generated_yaml)
        self.assertIn(salary, reloaded_budget)
        self.assertIn(rent, reloaded_budget)
        self.assertListEqual([salary, rent], list(reloaded_budget))

        reloaded_yaml = reloaded_budget.to_yaml()
        self.assertEqual(BUDGET_YAML_CONTENTS, reloaded_yaml)

    def test_save_load(self):
        budget = Budget()

        budget.add_item("Salary", 1000, "Every month starting on 5th November")
        budget.add_item("Rent", -500, "Every month starting on 20th November")

        with TemporaryDirectory() as tmp:
            path = Path(tmp).joinpath("budget.yaml")
            file = str(path)

            budget.save(file)

            file_contents = path.read_text(encoding="utf-8")
            self.assertEqual(budget.to_yaml(), file_contents)

            reloaded_budget = Budget.load(file)
            self.assertEqual(budget, reloaded_budget)
            self.assertEqual(budget.to_yaml(), reloaded_budget.to_yaml())
