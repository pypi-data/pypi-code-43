import click

from sqlalchemy import create_engine
from dbcache import schema


@click.group('dbcache')
def dbcache():
    pass


@dbcache.command('init-db')
@click.argument('dburi')
@click.option('--namespace', default='cache')
@click.option('--reset', is_flag=True, default=False)
def init_db(dburi, namespace, reset=False):
    engine = create_engine(dburi)
    schema.init(engine, ns=namespace, drop=reset)
