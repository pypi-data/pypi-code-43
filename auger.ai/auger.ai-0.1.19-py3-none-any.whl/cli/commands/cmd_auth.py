import click

from auger.api.auth import AugerAuth
from auger.cli.utils.context import pass_context


class AuthCmd(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def login(self, username, password, organization, url):
        AugerAuth(self.ctx).login(username, password, organization, url)

    def logout(self):

        AugerAuth(self.ctx).logout()

    def whoami(self):
        AugerAuth(self.ctx).whoami()


@click.group('auth', short_help='Authenticate with Auger Cloud.')
@pass_context
def command(ctx):
    """Authenticate with Auger Cloud."""
    ctx.setup_logger(format='')


@click.command(short_help='Login to Auger.')
@click.option(
    '--username', '-u', default=None, prompt='username',
    type=click.STRING, help='Auger username.')
@click.option(
    '--organization', '-o', default=None, prompt='organization',
    type=click.STRING, help='Auger organization.')
@click.password_option(
    '--password', '-p', prompt='password',
    confirmation_prompt=False, help='Auger password.')
@click.option(
    '--system', '-s', default='production',
    type=click.Choice(['production', 'staging']),
    help='Auger API endpoint.')
@pass_context
def login(ctx, username, password, organization, system):
    """Login to Auger."""
    urls = {
        'production': 'https://app.auger.ai',
        'staging': 'https://app-staging.auger.ai'}
    AuthCmd(ctx).login(username, password, organization, urls[system])


@click.command(short_help='Logout from Auger.')
@pass_context
def logout(ctx):
    """Logout from Auger."""
    AuthCmd(ctx).logout()


@click.command(short_help='Display the current logged in user.')
@pass_context
def whoami(ctx):
    """Display the current logged in user."""
    ctx.setup_logger(format='')
    AuthCmd(ctx).whoami()


@pass_context
def add_commands(ctx):
    command.add_command(login)
    command.add_command(logout)
    command.add_command(whoami)


add_commands()
