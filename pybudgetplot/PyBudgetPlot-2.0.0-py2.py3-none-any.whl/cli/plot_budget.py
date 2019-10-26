import sys
from pathlib import Path

from pbp.core import accountant, plotter
from pbp.core.budget import Budget


def main(args):
    file = args[0] if args else "budget.yaml"

    budget = Budget.load(file)
    print(budget.as_table(include_dates=True))

    data = accountant.calculate_data(budget)

    csv_file = str(Path.cwd().joinpath("budget.csv").resolve())
    print(f"Writing budget detailed data to '{csv_file}' ...")
    data.to_csv(csv_file, index_label="Date", encoding="utf-8")

    print("Plotting budget...")
    plotter.plot_data(data)


def run():
    args = sys.argv[1:]
    main(args)
