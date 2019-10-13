import click
from flask.cli import with_appcontext
from flask_security import utils

from .database import db
from .models import Role, User, Challenge, Solve


def drop_db():
    print("Dropping all tables from the database...")
    db.drop_all()
    db.session.commit()


def init_db():
    print("Creating all tables in the database and creating base user roles...")
    db.create_all()

    admin_role = Role(
        name="admin",
        description="Site admin")
    contestant_role = Role(
        name="contestant",
        description="CTF contestant")

    db.session.add(admin_role)
    db.session.add(contestant_role)
    db.session.commit()


def reset_db():
    print("Resetting the database...")
    drop_db()
    init_db()


def populate_test_data():
    print("Populating test data into the database...")
    from .models import User, RolesUsers, Challenge, Solve

    a_user = User(
        username="a",
        email="a@chiquito.com",
        password=utils.hash_password("b"),
        active=True)
    abc_user = User(
        username="abc",
        email="abc@chiquito.com",
        password=utils.hash_password("123"),
        active=True)

    db.session.add(a_user)
    db.session.add(abc_user)
    db.session.commit()

    a_contestant = RolesUsers(
        user_id=a_user.id,
        role_id=2)

    abc_admin = RolesUsers(
        user_id=abc_user.id,
        role_id=1)

    db.session.add(a_contestant)
    db.session.add(abc_admin)
    db.session.commit()

    first_challenge = Challenge(
        title="The First Challenge",
        category="crypto",
        body="Just think really hard!",
        hint="CTF{l0l}",
        solution="CTF{l0l}")
    second_challenge = Challenge(
        title="The Second Challenge",
        category="reversing",
        body="Just think really harder!",
        hint="no cheatin",
        solution="CTF{1337}")

    db.session.add(first_challenge)
    db.session.add(second_challenge)
    db.session.commit()

    a_first = Solve(
        user_id=a_user.id,
        challenge_id=first_challenge.id,
        solved=False,
        hinted=False,
    )
    a_second = Solve(
        user_id=a_user.id,
        challenge_id=second_challenge.id,
        solved=False,
        hinted=False,
    )
    abc_first = Solve(
        user_id=abc_user.id,
        challenge_id=first_challenge.id,
        solved=False,
        hinted=False,
    )
    abc_second = Solve(
        user_id=abc_user.id,
        challenge_id=second_challenge.id,
        solved=False,
        hinted=False,
    )
    db.session.add(a_first)
    db.session.add(a_second)
    db.session.add(abc_first)
    db.session.add(abc_second)
    db.session.commit()


@click.command('drop-db')
@with_appcontext
def drop_db_command():
    """Delete all tables from the database."""
    drop_db()
    click.echo('All tables dropped from the database.')


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Add all tables and roles to the database."""
    init_db()
    click.echo('All tables and roles added to the database.')


@click.command('reset-db')
@with_appcontext
def reset_db_command():
    """Delete all existing data and create new tables."""
    reset_db()
    click.echo('Reset the database.')


@click.command('populate-test-data')
@with_appcontext
def populate_test_data_command():
    """Populate the database with test data"""
    populate_test_data()
    click.echo('Inserted test data.')


@click.command('create-user')
@click.option('-u', '--username', prompt='Username', help='Username.')
@click.option('-e', '--email', prompt='Email', help='Email.')
@click.option('-p', '--password', prompt='Password', help='Password.')
@click.option('-r', '--role', default='', prompt='Role', help="Role. Must be 'admin', 'contestant', or ''.")
@with_appcontext
def create_user_command(username, email, password, role):
    """Creates a new user"""

    role = Role.query.filter_by(name=role).first()
    roles = [role] if role else []
    solves = [Solve(
        hinted=False,
        solved=False,
        challenge=challenge)
        for challenge in Challenge.query.all()]

    user = User(
        username=username,
        email=email,
        password=utils.hash_password(password),
        roles=roles,
        solves=solves,
        active=True)

    db.session.add(user)
    db.session.commit()

    click.echo('Inserted user ' + username)


@click.command('delete-user')
@click.option('-u', '--username', prompt='Username', help='The username of the user to delete.')
@with_appcontext
def delete_user_command(username):
    """Deletes a user"""
    from .models import User

    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        click.echo('Deleted user ' + username)
    else:
        click.echo('User ' + username + ' not found')


def init_app(app):
    app.cli.add_command(drop_db_command)
    app.cli.add_command(init_db_command)
    app.cli.add_command(reset_db_command)
    app.cli.add_command(populate_test_data_command)
    app.cli.add_command(create_user_command)
    app.cli.add_command(delete_user_command)
