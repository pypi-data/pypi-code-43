from pathlib import Path

from pbp.core.budget import Budget


def run():
    print()
    print(f"Initializing sample budget.yaml in '{str(Path.cwd().resolve())}' ...")
    print()
    file = str(Path.cwd().joinpath("budget.yaml").resolve())
    Budget.sample().save(file)
    print()
    print("All done!")
    print()
