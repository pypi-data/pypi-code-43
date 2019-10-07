import os
import webbrowser
from collections import namedtuple

import click

from rebotics_sdk.cli.common import shell, roles, configure, run
from rebotics_sdk.cli.utils import read_saved_role, process_role, ReboticsCLIContext, app_dir, pass_rebotics_context, \
    GroupWithOptionalArgument
from rebotics_sdk.providers import ProviderHTTPServiceException
from rebotics_sdk.providers.shelf_camera_manager import ShelfCameraManagerProvider


@click.group()
@click.option('-f', '--format', default='table', type=click.Choice(['table', 'id', 'json']), help='Result rendering')
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode')
@click.option('-c', '--config', type=click.Path(), default='shelf_camera.json', help="Specify what config.json to use")
@click.option('-r', '--role', default=lambda: read_saved_role('shelf_camera'), help="Key to specify what admin to use")
@click.version_option()
@click.pass_context
def api(ctx, format, verbose, config, role):
    """
    Admin CLI tool to communicate with dataset API
    """
    process_role(ctx, role, 'shelf_camera')
    ctx.obj = ReboticsCLIContext(
        role,
        format,
        verbose,
        os.path.join(app_dir, config),
        provider_class=ShelfCameraManagerProvider
    )


CameraType = namedtuple('CameraType', ['type', 'display', 'short'])
CAMERA_TYPES = [
    CameraType(0, 'Shelf Camera', 'shelf'),
    CameraType(1, 'Robot Camera', 'robot'),
    CameraType(2, 'End cap Camera', 'endcap'),
]


@api.group(cls=GroupWithOptionalArgument)
@click.argument('camera_settings_id', required=False)
@pass_rebotics_context
def camera_settings(ctx, camera_settings_id=None):
    if camera_settings_id:
        setattr(ctx, 'camera_settings_id', camera_settings_id)


@camera_settings.command(name='list')
@pass_rebotics_context
def camera_settings_list(ctx):
    ctx.format_result(ctx.provider.camera_settings_list(), keys_to_skip=['x_min', 'y_min', 'x_max', 'y_max'])


@camera_settings.command(name='detail')
@pass_rebotics_context
def camera_settings_detail(ctx):
    camera_settings_id = getattr(ctx, 'camera_settings_id', None)

    camera_settings = ctx.provider.camera_settings_detail(camera_settings_id)
    ctx.format_result(
        camera_settings,
        keys_to_skip=['x_min', 'y_min', 'x_max', 'y_max']
    )
    click.echo('Region of interest')
    ctx.format_result(camera_settings['region_of_interests'])


@camera_settings.command(name='view')
@pass_rebotics_context
def camera_settings_view(ctx):
    camera_settings_id = getattr(ctx, 'camera_settings_id', None)
    url = ctx.provider.build_url('/admin/fetcher/shelfcamerasettings/{}/change/'.format(camera_settings_id))

    if ctx.verbose:
        click.echo('Opening camera settings in browser: %s' % url)

    webbrowser.open(url)


@camera_settings.command(name='create')
@click.option('-t', '--token', help='Auth token for user to be used to send user')
@click.option('-s', '--store', help='Store ID')
@click.option('-r', '--retailer', help='Retailer codename')
@click.option('--rotation', help='Rotation: 0, 90, 180, 270', default=0)
@click.option('-t', '--camera_type', help='Camera type',
              type=click.Choice([t.short for t in CAMERA_TYPES]))
@click.argument('folder')
@pass_rebotics_context
def create_camera_settings(ctx, token, store, retailer, camera_type, folder, rotation):
    """Create camera settings with binding of stores and users and folder"""
    camera_type_codes = [c for c in CAMERA_TYPES if c.short == camera_type]
    if not camera_type_codes:
        raise click.ClickException('Camera type was not found')
    ct = camera_type_codes[0]
    try:
        if ctx.verbose:
            click.echo('Calling create camera settings')
        result = ctx.provider.add_camera_settings(
            retailer,
            store,
            token,
            ct.type,
            folder=folder,
            rotation=rotation
        )
        ctx.format_result(result, keys_to_skip=['x_min', 'y_min', 'x_max', 'y_max'])
        click.echo('Successfully added camera settings with id %d' % result['id'])
    except ProviderHTTPServiceException as exc:
        raise click.ClickException(str(exc))


@camera_settings.command(name='add-roi')
@click.option('-a', '--aisle')
@click.option('-s', '--section')
@click.option('-p', '--planogram_id')
@click.option('-c', '--coordinates')
@pass_rebotics_context
def camera_settings_add_roi(ctx, aisle, section, planogram_id, coordinates):
    camera_settings_id = getattr(ctx, 'camera_settings_id', None)
    if camera_settings_id is None:
        raise click.ClickException('You need to specify camera_settings_id. Usage: \n'
                                   'camera_manager camera-settings 123 add-roi')

    ctx.format_result(
        ctx.provider.add_camera_roi(camera_settings_id, 
                                    aisle=aisle,
                                    section=section,
                                    store_planogram_id=planogram_id,)
    )


api.add_command(shell, 'shell')
api.add_command(roles, 'roles')
api.add_command(configure, 'configure')
api.add_command(run, 'run')
