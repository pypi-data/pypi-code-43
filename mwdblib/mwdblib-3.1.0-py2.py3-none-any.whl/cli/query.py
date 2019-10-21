import click

from .authenticator import pass_mwdb
from .main import main


@main.command("query")
@click.argument("hash")
@pass_mwdb
def query(mwdb, hash):
    mwdb.query(hash)
