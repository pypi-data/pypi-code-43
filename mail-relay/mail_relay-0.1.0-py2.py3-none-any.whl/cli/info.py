import click
from mail_relay.store.handlers import read_config, read_users
from pvHelpers.cs_client import BACKEND_CLIENT
from pvHelpers.utils import CaseInsensitiveSet

from .context import ctx


@click.command()
@click.option('--org-info', 'show_org_info', flag_value=True, default=False)
@click.option('--export-group', 'show_export_group', flag_value=True, default=False)
@click.option('--members', 'show_members', flag_value=True, default=False)
@ctx
def info(ctx, show_org_info, show_export_group, show_members):
    '''Show information about organization, export groups and members.'''

    config = read_config(ctx.store.path)
    BACKEND_CLIENT.init(config.cs.http)

    users = [u for ((v, i), u) in read_users(ctx.store.path).iteritems() if v == -1]
    if len(users) == 0:
        click.echo('No users are configured! Try configuring exporter '
                   '```relay config exporter ...``` and try again.')
        return

    org_ids = CaseInsensitiveSet(
        filter(lambda i: i is not None, map(lambda u: u.org_info and u.org_info.org_id, users)))

    assert len(org_ids) == 1

    user, org_id = users[0], list(org_ids)[0]

    org_info = BACKEND_CLIENT.getOrgInfo(user, org_id)
    if (show_org_info or show_export_group or show_members) is False:  # show all if not specified
        click.echo(org_info)
    else:
        if show_org_info:  # get org info
            # latest user versions
            o = dict(org_info)
            del o['users']
            click.echo(o)

        # get export group info
        # get approvers/exporter info
        if show_export_group:
            if org_info['roled_approval_groups'].get('export_approval_group') is None:
                click.echo('No export group configured! Make sure to create and '
                           'set an export group for your organization and try again.')
                return
            group_id = org_info['roled_approval_groups']['export_approval_group']['group_id']
            version = org_info['roled_approval_groups']['export_approval_group']['version']
            export_group = BACKEND_CLIENT.getOrgAPGInfo(user, org_id, group_id, version)
            click.echo(export_group)

        # get members info
        if show_members:
            click.echo(org_info['users'])
