# -*- coding: utf-8 -*-

"""Console script for wcraas_discovery."""
import sys
import click

from wcraas_discovery import DiscoveryWorker
from wcraas_discovery.config import Config


@click.command()
def main(args=None):
    """Console script for wcraas_discovery."""
    worker = DiscoveryWorker(*Config.fromenv())
    worker.run()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
