import click
from tabulate import tabulate
from sqlalchemy.orm.exc import NoResultFound

from .db import get_db_connection, Aliases
from .helpers import split_email


@click.group()
def alias():
    pass


@click.command()
@click.pass_obj
def show(obj):
    """Lists all aliases."""
    conn = get_db_connection(obj)
    query = conn.query(Aliases).order_by(Aliases.id)
    result = [
        {'id': row.id,
         'source': f"{row.source_username}@{row.source_domain}",
         'destination': f"{row.destination_username}@{row.destination_domain}",
         'enabled': row.enabled,
         } for row in query]
    click.echo(tabulate(result, headers="keys"))
    return


@click.command()
@click.argument('source', type=click.STRING)
@click.argument('destination', type=click.STRING)
@click.option(
    '--enabled',
    '-e',
    type=click.BOOL,
    is_flag=True,
    help='Enable the alias.',
    default=False,
    show_default=True,
)
@click.pass_obj
def add(obj, source, destination, enabled):
    """Add an alias.
    
    Alias will be forwarding mails from SOURCE to DESTINATION.
    
    DESTINATION can also be external an email-address.
    """  # TODO: Check for collisions with users,
    src_username, src_domain = split_email(source)
    dest_username, dest_domain = split_email(destination)
    conn = get_db_connection(obj)

    new_alias = Aliases(
        source_username=src_username,
        source_domain=src_domain,
        destination_username=dest_username,
        destination_domain=dest_domain,
        enabled=enabled
    )

    conn.add(new_alias)

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    click.echo(f"Alias mapping from '{source}' to '{destination}' successfully created.")
    return


@click.command()
@click.argument('source', type=click.STRING)
@click.argument('destination', type=click.STRING)
@click.option(
    '--yes',
    'confirmation',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Delete alias without confirmation.'
)
@click.pass_obj
def remove(obj, source, destination, confirmation):
    """Delete an alias."""
    src_username, src_domain = split_email(source)
    dest_username, dest_domain = split_email(destination)
    conn = get_db_connection(obj)

    try:
        del_alias = conn.query(Aliases).filter_by(source_username=src_username, source_domain=src_domain, destination_username=dest_username, destination_domain=dest_domain).one()
    except NoResultFound:
        click.echo(f"Alias mapping from '{source}' to '{destination}' does not exist.")
        raise click.Abort

    if not confirmation:
        click.confirm(f"Are you sure you want to delete the alias mapping from '{source}' to '{destination}'?")

    conn.delete(del_alias)

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    click.echo(f"Alias mapping from '{source}' to '{destination}' was succesfully deleted.")
    return


alias.add_command(show)
alias.add_command(add)
alias.add_command(remove)
