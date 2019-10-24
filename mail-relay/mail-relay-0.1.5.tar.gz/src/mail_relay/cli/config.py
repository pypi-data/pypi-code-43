import click
from mail_relay.config import Config
from pvHelpers.utils import CaseInsensitiveSet

from .context import ctx


@click.group(invoke_without_command=True)
@click.option(
    '--config-file', 'config_file',
    envvar='CONFIG_FILE',
    type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def config(gctx, config_file):
    '''Show existing configiguration or re-config an existing setup.'''

    from mail_relay.store.handlers import read_config, update_config

    if gctx.invoked_subcommand is None:
        current_config = read_config(gctx.obj.store.path)
        if config_file is not None:
            if current_config is not None:
                click.echo('Current config:')
                click.echo(click.wrap_text(repr(current_config), initial_indent='>', subsequent_indent='>'))
                click.confirm('Would you like to re-config to {}?'.format(config_file))

            new_conf = Config.from_yaml(config_file)
            update_config(new_conf, gctx.obj.store.path)
        else:
            if current_config is None:
                click.echo('No config set, configure using --config-file!')
                # TODO: prompt user to input configs
            else:
                click.echo('Current config:')
                click.echo(click.wrap_text(repr(current_config), initial_indent='>', subsequent_indent='>'))


@click.command()
@click.option('--as-exporter', 'as_exporter', flag_value=True, default=False)
@click.option('-d', 'is_delete', flag_value=True, default=False)
@click.argument('user_id')
@ctx
def user(ctx, user_id, as_exporter, is_delete):
    '''Configure organization exporter account'''

    from mail_relay.store.handlers import (read_config, read_users, write_user, write_key,
                                           read_exporter, write_exporter, delete_user)
    all_users = read_users(ctx.store.path)
    if is_delete:
        delete_user(user_id, ctx.store.path)
        return

    click.echo('Configuring {} as {}'.format(user_id, 'exporter' if as_exporter else 'approver'))
    config = read_config(ctx.store.path)

    if user_id in CaseInsensitiveSet(map(lambda (v, i): i, all_users.iterkeys())):
        click.echo(
            'User {} exists locally! Please remove the user'
            ' ```relay config user -d ...``` and try again.'.format(user_id))

        return

    from mail_relay.secure_channel import GetMessageManager, TransferTypes
    from pvHelpers.crypto import PVKeyFactory
    from pvHelpers.request import DeviceRequest
    from pvHelpers.user import LocalUser, LocalDevice
    from pvHelpers.utils import NOT_ASSIGNED

    def verifier(pin):
        click.echo('Verification pin: {}'.format(pin))
        return True

    def callback(transferred_user_key, device_req_signature):
        user_key = PVKeyFactory.deserializeUserKey(transferred_user_key, is_protobuf=False)
        auth_user = LocalUser(
            user_id, -153, user_id, u'', None, NOT_ASSIGNED(), u'', [user_key], device_req.device)

        # get user information from server
        from pvHelpers.cs_client import BACKEND_CLIENT

        BACKEND_CLIENT.init(config.cs.http)
        u = BACKEND_CLIENT.fetchUsers(auth_user, [(auth_user.user_id, -1)])[auth_user.user_id]
        user = LocalUser(
                u.user_id, u.account_version, u.display_name, u.mail_cid,
                u.org_info, NOT_ASSIGNED(), u'', [user_key], device_req.device)

        write_key(user.user_id, user.account_version, user_key, ctx.store.path)
        write_user(user, ctx.store.path)
        if as_exporter is True:
            exporter_id, account_version = read_exporter(ctx.store.path)
            if exporter_id is not None:
                click.confirm(
                    '{} is current exporter, would you like to re-config setting '
                    '{} as exporter?'.format((exporter_id, account_version), (user.user_id, user.account_version)))

            write_exporter(user.user_id, user.account_version, ctx.store.path)

        return True

    device_req = DeviceRequest.newForTransfer(user_id, LocalDevice.newDevice())
    manager = GetMessageManager(
        config.cs.ws, user_id, user_id, TransferTypes.TRANSFER, verifier, callback)

    # test blocks here till `callback` function returns
    manager.get_secure_channel(new_device_req=device_req)


@click.command()
@click.argument('user_id')
@click.pass_context
def exporter(ctx, user_id):
    '''Configure organization export group expoter account'''

    ctx.invoke(user, user_id=user_id, as_exporter=True)


@click.command()
@click.argument('user_id')
@click.pass_context
def approver(ctx, user_id):
    '''Configure organization export group approver accounts'''

    ctx.invoke(user, user_id=user_id, as_exporter=False)


config.add_command(exporter)
config.add_command(approver)
config.add_command(user)
