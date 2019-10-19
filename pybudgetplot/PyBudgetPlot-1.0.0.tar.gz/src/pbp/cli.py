import sys

from pbp import plotter
from pbp.datamodel import Budget


def main(args):
    file = args[0]
    print(f"Loading budget from: '{file}'")

    budget = Budget.load(file)
    print(budget)

    print("Plotting budget...")
    plotter.plot_budget(budget)


def run():
    args = sys.argv[1:]
    main(args)


if __name__ == '__main__':
    run()
