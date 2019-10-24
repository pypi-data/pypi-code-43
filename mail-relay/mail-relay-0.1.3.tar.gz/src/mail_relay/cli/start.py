import time

import click
from mail_relay.store.handlers import read_config, read_users
from .context import ctx


@click.command()
@ctx
def start(ctx):
    '''Start relay daemon.'''

    while True:
        print read_users(ctx.store.path)
        time.sleep(1)

