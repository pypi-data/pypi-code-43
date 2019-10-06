import click
from sqlalchemy.orm.exc import NoResultFound
from tabulate import tabulate

from .db import get_db_connection, Domains


@click.group()
def domain():
    pass


@click.command()
@click.pass_obj
def show(obj):
    """Lists all domains."""
    conn = get_db_connection(obj)
    query = conn.query(Domains).order_by(Domains.id)
    result = [{'id': row.id, 'domain': row.domain} for row in query]
    click.echo(tabulate(result, headers="keys"))
    return


@click.command()
@click.argument('domain', type=click.STRING)
@click.pass_obj
def add(obj, domain):
    """Add a domain."""
    conn = get_db_connection(obj)
    new_domain = Domains(domain=domain)
    conn.add(new_domain)
    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort
    click.echo(f"Domain '{domain}' was successfully added.")
    return


@click.command()
@click.argument('domain', type=click.STRING)
@click.option(
    '--yes',
    'confirmation',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Delete domain without confirmation.'
)
@click.pass_obj
def remove(obj, domain, confirmation):
    """Delete a domain."""  # TODO: Check for existing accounts / aliases
    conn = get_db_connection(obj)

    try:
        del_domain = conn.query(Domains).filter_by(domain=domain).one()
    except NoResultFound:
        click.echo(f"Domain '{domain}' does not exist.")
        raise click.Abort

    if not confirmation:
        click.confirm(f"Are you sure you want to delete the account '{domain}'?", abort=True)

    conn.delete(del_domain)

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    click.echo(f"Domain '{domain}' was succesfully deleted.")
    return


domain.add_command(show)
domain.add_command(add)
domain.add_command(remove)
