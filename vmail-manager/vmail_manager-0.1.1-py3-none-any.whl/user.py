import click
from sqlalchemy.orm.exc import NoResultFound
from tabulate import tabulate

from .db import get_db_connection, Accounts
from .helpers import split_email, gen_password_hash


@click.group()
def user():
    pass


@click.command()
@click.pass_obj
def show(obj):
    """List all users."""
    conn = get_db_connection(obj)
    query = conn.query(Accounts).order_by(Accounts.id)
    result = [
        {'id': row.id,
         'email': f"{row.username}@{row.domain}",
         'password': row.password,
         'quota': row.quota,
         'enabled': row.enabled,
         'sendonly': row.sendonly
         } for row in query]
    click.echo(tabulate(result, headers="keys"))
    return


@click.command()
@click.argument('email', type=click.STRING)
@click.password_option()
@click.option(
    '--quota',
    '-q',
    type=click.INT,
    help='Maildir quota for the account. Set 0 for unlimited storage.',
    default=2048,
    show_default=True,
)
@click.option(
    '--enabled',
    '-e',
    type=click.BOOL,
    help='Enable the account directly.',
    default=False,
    show_default=True,
)
@click.option(
    '--sendonly',
    '-s',
    type=click.BOOL,
    is_flag=True,
    help='Make account send only. So receiving of mails is not possible.',
    default=False,
    show_default=True,
)
@click.pass_obj
def add(obj, email, password, quota, enabled, sendonly):
    """Add an user."""  # TODO: Check for collisions with aliases
    username, domain = split_email(email)
    if sendonly:
        quota = 0  # Send-only accounts don't need quota settings.

    conn = get_db_connection(obj)
    pw_hash = gen_password_hash(password)
    new_user = Accounts(username=username,
                        domain=domain,
                        password=pw_hash,
                        quota=quota,
                        enabled=enabled,
                        sendonly=sendonly)

    conn.add(new_user)

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    click.echo(f"User '{email}' was successfully added.")

    return


@click.command()
@click.argument('email', type=click.STRING)
@click.option(
    '--quota',
    '-q',
    type=click.INT
)
@click.option(
    '--sendonly',
    '-s',
    type=click.BOOL
)
@click.option(
    '--yes',
    'confirmation',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Edit user without confirmation.'
)
@click.pass_obj
def edit(obj, email, quota, sendonly, confirmation):
    """Edits an user."""  # TODO: DOC
    username, domain = split_email(email)
    conn = get_db_connection(obj)

    try:
        edit_user = conn.query(Accounts).filter_by(username=username, domain=domain).one()
    except NoResultFound:
        click.echo(f"User '{email}' does not exist.")
        raise click.Abort

    if sendonly is not None:
        if not confirmation:
            click.confirm(f"Change sendonly flag of user '{email}' from {edit_user.sendonly} to {sendonly}?", abort=True)
        edit_user.sendonly = sendonly
        if sendonly:
            edit_user.quota = 0
        if not sendonly and quota is None and edit_user.quota is 0:
            if not click.confirm(f"User '{email}' will have unlimited quota, are you shure?"):
                quota = click.prompt(f"Enter new quota for user '{email}' in MB", type=click.INT)

    if quota is not None:
        if not confirmation:
            click.confirm(f"Change quota of user '{email}' from {edit_user.quota} MB to {quota} MB?", abort=True)
        edit_user.quota = quota

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    return


@click.command()
@click.argument('email', type=click.STRING)
@click.password_option(prompt='Enter new password')
@click.pass_obj
def passwd(obj, email, password):
    """Changes password of user."""
    username, domain = split_email(email)
    conn = get_db_connection(obj)

    try:
        edit_user = conn.query(Accounts).filter_by(username=username, domain=domain).one()
    except NoResultFound:
        click.echo(f"User '{email}' does not exist.")
        raise click.Abort

    edit_user.password = gen_password_hash(password)

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    click.echo(f"Password of user '{email}' successfully changed.")
    return


@click.command()
@click.argument('email', type=click.STRING)
@click.option(
    '--yes',
    'confirmation',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Enable user without confirmation.'
)
@click.pass_obj
def enable(obj, email, confirmation):
    """Enables an user."""
    username, domain = split_email(email)
    conn = get_db_connection(obj)

    try:
        edit_user = conn.query(Accounts).filter_by(username=username, domain=domain).one()
    except NoResultFound:
        click.echo(f"User '{email}' does not exist.")
        raise click.Abort

    if edit_user.enabled:
        click.echo(f"User '{email}' is already enabled.")
        raise click.Abort

    if not confirmation:
        click.confirm(f"Are you sure you want to enable the account '{email}'?", abort=True)

    edit_user.enabled = True

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    click.echo(f"User '{email}' successfully enabled.")
    return


@click.command()
@click.argument('email', type=click.STRING)
@click.option(
    '--yes',
    'confirmation',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Disable user without confirmation.'
)
@click.pass_obj
def disable(obj, email, confirmation):
    """Disables an user."""
    username, domain = split_email(email)
    conn = get_db_connection(obj)

    try:
        edit_user = conn.query(Accounts).filter_by(username=username, domain=domain).one()
    except NoResultFound:
        click.echo(f"User '{email}' does not exist.")
        raise click.Abort

    if not edit_user.enabled:
        click.echo(f"User '{email}' is already disabled.")
        raise click.Abort

    if not confirmation:
        click.confirm(f"Are you sure you want to disable the account '{email}'?")
    edit_user.enabled = False

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    click.echo(f"User '{email}' successfully disabled.")
    return


@click.command()
@click.argument('email', type=click.STRING)
@click.option(
    '--yes',
    'confirmation',
    type=click.BOOL,
    is_flag=True,
    default=False,
    help='Delete user without confirmation.'
)
@click.pass_obj
def remove(obj, email, confirmation):
    """Removes an user."""  # TODO: Check for existing aliases
    username, domain = split_email(email)
    conn = get_db_connection(obj)

    try:
        del_user = conn.query(Accounts).filter_by(username=username, domain=domain).one()
    except NoResultFound:
        click.echo(f"User '{email}' does not exist.")
        raise click.Abort

    if not confirmation:
        click.confirm(f"Are you sure you want to delete the account '{email}'?")

    conn.delete(del_user)

    try:
        conn.commit()
    except Exception as e:
        click.echo(e)
        raise click.Abort

    click.echo(f"User '{email}' was successfully deleted.")
    return


user.add_command(show)
user.add_command(add)
user.add_command(edit)
user.add_command(passwd)
user.add_command(enable)
user.add_command(disable)
user.add_command(remove)
