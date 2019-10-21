"""
Connect to ANTARES' Kafka cluster and read messages.

"""
import click

import antares_client
from . import log
from .commands.search import search
from .commands.stream import stream

logger = log.setup_logger("cli")


@click.group()
@click.version_option(antares_client.__version__)
def entry_point():
    pass


entry_point.add_command(search)
entry_point.add_command(stream)
