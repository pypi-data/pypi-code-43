import time

import click
from mail_relay.store.handlers import read_users

from .context import ctx


@click.command()
@ctx
def start(ctx):
    '''Start relay daemon.'''

    while True:
        try:
            print read_users(ctx.store.path)
        except Exception as e:
            print e
        finally:
            time.sleep(1)
