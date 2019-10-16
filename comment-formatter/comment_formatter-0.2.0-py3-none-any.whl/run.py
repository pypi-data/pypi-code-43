from glob import glob
import os

import click

from .formatter import rewrite_file


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--line-length", type=int, default=100)
def run(path: str, line_length: int) -> None:
    """CLI for comment formatting"""
    if os.path.isdir(path):
        python_files = glob(os.path.join(path, "**/*.py"), recursive=True)
    else:
        python_files = [path]

    for file_name in python_files:
        rewrite_file(file_name)


if __name__ == "__main__":
    run()
