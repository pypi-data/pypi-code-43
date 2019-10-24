import click

from mail_relay.store import DEFAULT_STORE_PATH, Store

from .config import config
from .context import Context, ctx
from .info import info
from .start import start
from .status import status


@click.group()
@click.option(
    '-p', '--store-path', 'store_path',
    type=click.Path(dir_okay=False),
    default=DEFAULT_STORE_PATH, show_default=True,
    help='Path to sqlite store.')
@click.option(
    '--store-version', 'store_version',
    type=click.INT,
    default=0, show_default=True,
    help='sqlite store version.')
@click.pass_context
def driver(ctx, store_path, store_version):
    '''relay is a simple cli tool that relays preveil emails to a configurable smtp server'''

    # Initiate context object
    ctx.obj = Context(Store(store_path, store_version))


@click.command()
@ctx
def migrate(ctx):
    '''Migrate database using mail_rely/migrate.py (or optional script).'''
    # TODO dynamic migrate script
    from mail_relay.store.migrate import migrate
    migrate(ctx.store.path)


driver.add_command(info)
driver.add_command(config)
driver.add_command(migrate)
driver.add_command(start)
driver.add_command(status)
