import click
import clickclick
import requests
import time

import zalando_aws_cli
import zalando_aws_cli.api

from clickclick import Action, AliasedGroup, print_table, OutputFormat


output_option = click.option('-o', '--output', type=click.Choice(['text', 'json', 'tsv']), default='text',
                             help='Use alternative output format')


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('{command} {version}'.format(command=ctx.info_name, version=zalando_aws_cli.__version__))
    ctx.exit()


@click.group(cls=AliasedGroup, invoke_without_command=True, context_settings={'help_option_names': ['-h', '--help']})
@click.option('-V', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='Print the current version number and exit.')
@click.option('--awsprofile', help='Profilename in ~/.aws/credentials', default='default', show_default=True)
@click.pass_context
def cli(ctx, awsprofile):
    ctx.obj = zalando_aws_cli.api.load_config()

    if 'service_url' not in ctx.obj:
        configure_service_url()
        ctx.obj = zalando_aws_cli.api.load_config()

    if not ctx.invoked_subcommand:
        ctx.invoke(login)


def get_matching_profiles(profiles: list, search_string: str) -> list:
    matches = []
    for profile in profiles:
        if profile['account_name'] == search_string \
           or profile['role_name'] == search_string or profile['account_id'] == search_string:
            matches.append(profile)
    return matches


def find_profile(config, token, args):
    """Returns the profile from the list of arguments. Supports the following:
         - [] (resolves to default if set, otherwise to the last account used)
         - [ALIAS]
         - [ACCOUNT] if the corresponding account has just one role
         - [ACCOUNT, ROLE]"""

    if len(args) == 0:
        if 'default' in config:
            account_name = config['default']['account_name']
            role_name = config['default']['role_name']
        elif 'last_update' in config:
            account_name = config['last_update']['account_name']
            role_name = config['last_update']['role_name']
        else:
            raise click.UsageError('No default profile. Use "zaws set-default..." to set a default profile.')
    elif len(args) == 1:
        target = args[0]

        alias = config.get('aliases', {}).get(target)

        if alias:
            account_name = alias['account_name']
            role_name = alias['role_name']
        else:
            profiles = zalando_aws_cli.api.get_roles(token)
            matching_profiles = [profile for profile in profiles if target in profile]

            if len(matching_profiles) == 1:
                return matching_profiles[0]
            elif len(matching_profiles) > 1:
                raise click.UsageError('More than 1 profile matching {}'.format(target))
            else:
                raise click.UsageError('No roles found matching "{}"'.format(target))
    else:
        account_name = args[0]
        role_name = args[1]

    profile = get_role(token, account_name, role_name)
    if not profile:
        raise click.UsageError('No roles found matching {}'.format(' '.join(args)))
    return profile


@cli.command()
@click.argument('account-role-or-alias', nargs=-1)
@click.option('-r', '--refresh', is_flag=True, help='Keep running and refresh access tokens automatically')
@click.option('--awsprofile', help='Profilename in ~/.aws/credentials', default='default', show_default=True)
@click.pass_obj
def login(obj, account_role_or_alias, refresh, awsprofile):
    '''Login to AWS with given account and role. An alias can also be used.

    If the user has only one role, only the AWS account is needed.'''

    token = zalando_aws_cli.api.get_token()
    profile = find_profile(obj, token, account_role_or_alias)

    while True:
        credentials = zalando_aws_cli.api.get_credentials(token, profile.account_id, profile.role_name)

        last_updated = time.time()

        with Action('Writing temporary AWS credentials for {} {}..'.format(profile.account_name, profile.role_name)):
            zalando_aws_cli.api.persist_credentials(credentials, awsprofile)

            obj['last_update'] = {'account_name':   profile.account_name,
                                  'role_name':      profile.role_name,
                                  'timestamp':      last_updated}
            zalando_aws_cli.api.store_config(obj)

        if not refresh:
            break

        wait_time = 3600 * 0.9
        next_update = last_updated + wait_time

        with Action('Waiting {} minutes before refreshing credentials..'
                    .format(round((next_update - time.time()) / 60))) as act:
            try:
                while time.time() < next_update:
                    time.sleep(120)
                    act.progress()
            except KeyboardInterrupt:
                # do not show "EXCEPTION OCCURRED" for CTRL+C
                break

        # Refresh the access token
        token = zalando_aws_cli.api.get_token()


@cli.command()
@click.argument('account-role-or-alias', nargs=-1)
@click.option('--awsprofile', help='Profilename in ~/.aws/credentials', default='default', show_default=True)
@click.pass_context
def require(ctx, account_role_or_alias, awsprofile):
    '''Login if necessary'''

    token = zalando_aws_cli.api.get_token()
    profile = find_profile(ctx.obj, token, account_role_or_alias)

    last_update = ctx.obj['last_update'] if 'last_update' in ctx.obj else {}

    last_account_name = last_update.get('account_name')
    last_role_name = last_update.get('role_name')

    time_remaining = last_update['timestamp'] + 3600 * 0.9 - time.time() if last_update else 0

    if (time_remaining <= 0 or (profile.account_name, profile.role_name) != (last_account_name, last_role_name)):
        ctx.invoke(login, account_role_or_alias=account_role_or_alias, refresh=False, awsprofile=awsprofile)


@cli.command()
@output_option
@click.pass_obj
def list(obj, output):
    '''List AWS profiles'''

    token = zalando_aws_cli.api.get_token()
    role_list = [role._asdict() for role in zalando_aws_cli.api.get_roles(token)]

    default = obj['default'] if 'default' in obj else {}

    if 'aliases' in obj:
        alias_list = {(v['account_name'], v['role_name']): alias for alias, v in obj['aliases'].items()}
    else:
        alias_list = {}

    for role in role_list:
        if (default and
                (role['account_name'], role['role_name']) == (default['account_name'], default['role_name'])):
            role['default'] = '✓'
        else:
            role['default'] = ''

        if (role['account_name'], role['role_name']) in alias_list:
            role['alias'] = alias_list[(role['account_name'], role['role_name'])]
        else:
            role['alias'] = ''

    role_list.sort(key=lambda r: r['account_name'])

    with OutputFormat(output):
        print_table(['account_id', 'account_name', 'role_name', 'alias', 'default'], role_list)


@cli.command()
@click.argument('alias')
@click.argument('account-name')
@click.argument('role-name')
@click.pass_obj
def alias(obj, alias, account_name, role_name):
    '''Set an alias to an account and role name.'''

    token = zalando_aws_cli.api.get_token()
    profile = get_role(token, account_name, role_name)
    if not profile:
        raise click.UsageError('Profile "{} {}" does not exist'.format(account_name, role_name))

    if 'aliases' not in obj:
        obj['aliases'] = {}

    # Prevent multiple aliases for same account
    obj['aliases'] = {k: v for k, v in obj['aliases'].items()
                      if (v['account_name'], v['role_name']) != (account_name, role_name)}

    obj['aliases'][alias] = {'account_name': account_name, 'role_name': role_name}
    zalando_aws_cli.api.store_config(obj)

    click.echo('You can now get AWS credentials to {} {} with "zaws login {}".'.format(account_name, role_name, alias))


@cli.command('set-default')
@click.argument('account-name')
@click.argument('role-name')
@click.pass_obj
def set_default(obj, account_name, role_name):
    '''Set default AWS account role'''

    token = zalando_aws_cli.api.get_token()

    profile = get_role(token, account_name, role_name)
    if not profile:
        raise click.UsageError('Profile "{} {}" does not exist'.format(account_name, role_name))

    obj['default'] = {'account_name': profile.account_name, 'role_name': profile.role_name}
    zalando_aws_cli.api.store_config(obj)

    click.echo('Default account role set to {} {}'.format(account_name, role_name))


def get_role(token, account_name, role_name):
    '''Get the role with the provided account name and role name, or None if none match'''
    roles = zalando_aws_cli.api.get_roles(token)

    for item in roles:
        if item.account_name == account_name and item.role_name == role_name:
            return item

    return None


def configure_service_url():
    '''Prompts for the Credential Service URL and writes in local configuration'''

    # Keep trying until successful connection
    while True:
        service_url = click.prompt('Enter credentials service URL')
        if not service_url.startswith('http'):
            service_url = 'https://{}'.format(service_url)
        try:
            r = requests.get(service_url + '/swagger.json', timeout=2)
            if r.status_code == 200:
                break
            else:
                click.secho('ERROR: no response from credentials service', fg='red', bold=True)
        except requests.exceptions.RequestException:
            click.secho('ERROR: connection error or timed out', fg='red', bold=True)

    config = zalando_aws_cli.api.load_config()
    config['service_url'] = service_url
    zalando_aws_cli.api.store_config(config)


def main():
    try:
        cli()
    except Exception as e:
        clickclick.error(e)
