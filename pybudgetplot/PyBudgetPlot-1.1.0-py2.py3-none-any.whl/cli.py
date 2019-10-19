import sys

import pbp.core.accountant
from pbp.core import plotter
from pbp.core.budget import Budget


def main(args):
    file = args[0]
    budget = Budget.load(file)
    print(budget)

    pbp.core.accountant.export_budget_data(budget, "budget.csv")
    print("Plotting budget...")
    plotter.plot_budget(budget)


def run():
    args = sys.argv[1:]
    main(args)


if __name__ == '__main__':
    run()
