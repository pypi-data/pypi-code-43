import click
import confuse
import sqlalchemy.dialects

from .alias import alias
from .domain import domain
from .user import user

cfg = confuse.Configuration('vmail-manager', __name__)


@click.group(context_settings=dict(max_content_width=120))
@click.option(
    '--dialect',
    type=click.Choice(sqlalchemy.dialects.__all__),
    help='Dialect of the Database.',
)
@click.option(
    '--driver',
    type=click.STRING,
    help='Driver to connect to the database host.',
)
@click.option(
    '--host',
    '-h',
    type=click.STRING,
    help='Hostname of the database host.',
)
@click.option(
    '--port',
    '-p',
    type=click.INT,
    help='Port number of Database host.',
)
@click.option(
    '--username',
    '-u',
    type=click.STRING,
)
@click.option(
    '--password',
    '-p',
    type=click.STRING,
    help='Provide password via cli. If no value is given, prompt for entering password will be shown.'
)
@click.option(
    '--database',
    '-d',
    type=click.STRING,
    help='Name of the database',
)
@click.pass_context
def cli(ctx, dialect, driver, host, port, username, password, database):
    """Management of database for vmail-setup.

    User config is loaded from ~/.config/vmail-manager/config.yaml.
    Priority of options are OPTIONS > USER-CONFIG > DEFAULTS.

    """
    for param in [('dialect', dialect), ('driver', driver), ('host', host), ('port', port), ('username', username),
                  ('password', password), ('database', database)]:
        if param[1] is not None:
            cfg['DB'][param[0]] = param[1]

    if cfg['DB']['password'].get() is None:
        cfg['DB']['password'] = click.prompt("Password", hide_input=True)

    ctx.obj = cfg
    pass


cli.add_command(domain)
cli.add_command(user)
cli.add_command(alias)
