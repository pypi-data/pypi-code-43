# -*- coding: utf-8 -*-

"""Console script for wcraas_storage."""
import sys
import click

from wcraas_storage import StorageWorker, Config


@click.command()
def main(args=None):
    worker = StorageWorker(*Config.fromenv())
    worker.run()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
