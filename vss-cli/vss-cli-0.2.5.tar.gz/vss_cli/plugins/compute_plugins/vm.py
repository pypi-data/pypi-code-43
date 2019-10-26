import datetime
import logging
import os

import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.exceptions import VssCliError
from vss_cli.helper import (
    format_output, process_filters, raw_format_output, to_tuples)
from vss_cli.plugins.compute import cli
from vss_cli.plugins.compute_plugins import rel_opts as c_so
from vss_cli.validators import (
    validate_email, validate_json_type, validate_phone_number)

_LOGGING = logging.getLogger(__name__)


@with_plugins(iter_entry_points('vss_cli.contrib.compute.vm'))
@cli.group('vm', short_help='Manage virtual machines')
@pass_context
def compute_vm(ctx: Configuration):
    """List, update, deploy and delete instances."""
    pass


@compute_vm.command('ls', short_help='List virtual machine')
@so.filter_opt
@so.all_opt
@so.page_opt
@so.sort_opt
@so.count_opt
@pass_context
def compute_vm_ls(ctx: Configuration, filter_by, show_all, sort, page, count):
    """List virtual machine instances.

        Filter and sort list by any attribute. For example:

        vss-cli compute vm ls -f name like,%vm-name% -f version like,%13

        Simple name filtering:

        vss-cli compute vm ls -f name %vm-name% -s name desc

    """
    params = dict(expand=1, sort='name,asc')
    if all(filter_by):
        params['filter'] = ','.join(process_filters(filter_by))
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # get templates
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_vms(show_all=show_all, per_page=count, **params)
    # including additional attributes?
    columns = ctx.columns or const.COLUMNS_VM
    # format output
    output = format_output(ctx, obj, columns=columns)
    # page
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@compute_vm.group(
    'get',
    short_help='Given virtual machine info.',
    invoke_without_command=True,
)
@click.argument(
    'uuid_or_name',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.virtual_machines,
)
@pass_context
def compute_vm_get(ctx: Configuration, uuid_or_name):
    """Obtain virtual machine summary and other attributes."""
    _vm = ctx.get_vm_by_uuid_or_name(uuid_or_name)
    ctx.uuid = _vm[0]['uuid']
    if click.get_current_context().invoked_subcommand is None:
        columns = ctx.columns or const.COLUMNS_VM_INFO
        obj = ctx.get_vm(ctx.uuid)
        if not obj:
            raise VssCliError('Virtual Machine not found')
        click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('admin', short_help='Admin (metadata)')
@pass_context
def compute_vm_get_admin(ctx: Configuration,):
    """Virtual machine administrator. Part of the
    VSS metadata."""
    columns = ctx.columns or const.COLUMNS_VM_ADMIN
    obj = ctx.get_vm_vss_admin(ctx.uuid)
    if not obj:
        raise VssCliError('Virtual Machine Admin not found')
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('alarm', short_help='Triggered alarms')
@click.argument('moref', type=click.STRING, required=False)
@pass_context
def compute_vm_get_alarms(ctx: Configuration, moref):
    """Virtual machine triggered alarms"""
    if moref:
        columns = ctx.columns or const.COLUMNS_VM_ALARM
        obj = ctx.get_vm_alarm(ctx.uuid, moref)
        obj = obj or []
        click.echo(format_output(ctx, obj, columns=columns, single=True))
    else:
        columns = ctx.columns or const.COLUMNS_VM_ALARM
        obj = ctx.get_vm_alarms(ctx.uuid)
        obj = obj or []
        click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('boot', short_help='Boot configuration')
@pass_context
def compute_vm_get_boot(ctx: Configuration,):
    """Virtual machine boot settings.
       Including boot delay and whether or not
       to boot and enter directly to BIOS."""
    columns = ctx.columns or const.COLUMNS_VM_BOOT
    obj = ctx.get_vm_boot(ctx.uuid)
    obj = obj or {}
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('cd', short_help='CD/DVD configuration')
@click.argument('unit', type=int, required=False)
@pass_context
def compute_vm_get_cds(ctx: Configuration, unit):
    """Virtual machine CD/DVD configuration."""
    if unit:
        obj = ctx.get_vm_cd(ctx.uuid, unit)
        if obj:
            columns = ctx.columns or const.COLUMNS_VM_CD
            click.echo(format_output(ctx, obj, columns=columns, single=True))
        else:
            logging.error('Unit does not exist')
    else:
        devs = ctx.get_vm_cds(ctx.uuid)
        obj = [d.get('data') for d in devs] if devs else []
        columns = ctx.columns or const.COLUMNS_VM_CD_MIN
        click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('client', short_help='Client (Metadata)')
@pass_context
def compute_vm_get_client(ctx: Configuration):
    """Get current virtual machine client/billing department.
    Part of the VSS metadata.
    """
    obj = ctx.get_vm_vss_client(ctx.uuid)
    columns = ctx.columns or [('value',)]
    obj = obj or {}
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('client-note', short_help='Client note (Metadata)')
@pass_context
def compute_vm_get_client_notes(ctx):
    """Virtual machine client notes. Part of the
    VM metadata."""
    obj = ctx.get_vm_notes(ctx.uuid)
    columns = ctx.columns or [('value',)]
    obj = obj or {}
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('console', short_help='Virtual machine console link')
@click.option(
    '-l', '--launch', is_flag=True, help='Launch link to default handler'
)
@click.option(
    '-c',
    '--client',
    type=click.Choice(['html5', 'flex', 'vmrc']),
    help='Client type to generate link.',
    default='flex',
    show_default=True,
)
@pass_context
def compute_vm_get_console(ctx: Configuration, launch, client):
    """'Get one-time HTML link to access console"""
    username = ctx.username or click.prompt(
        'Username', default=os.environ.get('VSS_USER', '')
    )
    password = ctx.password or click.prompt(
        'Password',
        default=os.environ.get('VSS_USER_PASS', ''),
        show_default=False,
        hide_input=True,
        confirmation_prompt=True,
    )
    auth = (username.decode(), password.decode())
    obj = ctx.get_vm_console(ctx.uuid, auth=auth, client=client)
    link = obj.get('value')
    # print
    columns = ctx.columns or [('value',)]
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # launch
    if launch:
        click.launch(link)


@compute_vm_get.command('consolidate', short_help='Consolidation requirement')
@pass_context
def compute_vm_get_consolidate(ctx):
    """Virtual Machine disk consolidation status."""
    obj = ctx.get_vm_consolidation(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_VM_CONSOLIDATION
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.group('controller', invoke_without_command=True)
@pass_context
def compute_vm_get_controllers(ctx: Configuration):
    """Controllers (IDE, SCSI, etc.)"""
    if click.get_current_context().invoked_subcommand is None:
        obj = ctx.get_vm_controllers(ctx.uuid)
        obj = obj or {}
        columns = ctx.columns or const.COLUMNS_VM_CONTROLLERS
        click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get_controllers.command('scsi', short_help='SCSI adapters')
@click.argument('bus', type=click.INT, required=False)
@click.option('--disks', '-d', help='include disks attached', is_flag=True)
@pass_context
def compute_vm_get_controller_scsi(ctx: Configuration, bus, disks):
    """Virtual machine SCSI controllers and attached disks"""
    if bus is None:
        obj = ctx.get_vm_scsi_devices(ctx.uuid)
        columns = ctx.columns or const.COLUMNS_VM_CTRL_MIN
        click.echo(format_output(ctx, obj, columns=columns))
    else:
        obj = ctx.get_vm_scsi_device(ctx.uuid, bus, disks)
        if disks:
            obj = obj.get('devices', [])
            columns = ctx.columns or const.COLUMNS_VM_CTRL_DISK
            click.echo(format_output(ctx, obj, columns=columns))
        else:
            columns = ctx.columns or const.COLUMNS_VM_CTRL
            click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('cpu', short_help='CPU configuration')
@pass_context
def compute_vm_get_cpu(ctx: Configuration):
    """Virtual machine cpu configuration.
    Get CPU count and quick stats."""
    columns = ctx.columns or const.COLUMNS_VM_CPU
    obj = ctx.get_vm_cpu(ctx.uuid)
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('description', short_help='Description (Metadata)')
@pass_context
def compute_vm_get_description(ctx: Configuration):
    """Virtual machine description. Part of the
    VSS metadata."""
    obj = ctx.get_vm_vss_description(ctx.uuid)
    # print
    columns = ctx.columns or [('value',)]
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.group(
    'disk', short_help='Disk configuration', invoke_without_command=True
)
@click.argument('unit', type=click.INT, required=False)
@pass_context
def compute_vm_get_disks(ctx: Configuration, unit):
    """Virtual machine Disk configuration."""
    ctx.unit = unit
    if click.get_current_context().invoked_subcommand is None:
        if ctx.unit:
            obj = ctx.get_vm_disk(ctx.uuid, ctx.unit)
            if obj:
                columns = ctx.columns or const.COLUMNS_VM_DISK
                click.echo(
                    format_output(ctx, obj, columns=columns, single=True)
                )
            else:
                logging.error('Unit does not exist')
        else:
            obj = ctx.get_vm_disks(ctx.uuid)
            obj = [d.get('data') for d in obj] if obj else []
            columns = ctx.columns or const.COLUMNS_VM_DISK_MIN
            click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get_disks.command('backing', short_help='backing info')
@pass_context
def compute_vm_get_disks_backing(ctx: Configuration):
    """Virtual disk backing info"""
    columns = ctx.columns or const.COLUMNS_VM_DISK_BACKING
    obj = ctx.get_vm_disk_backing(ctx.uuid, ctx.unit)
    if obj:
        click.echo(format_output(ctx, [obj], columns=columns, single=True))
    else:
        logging.error('Disk %s backing could not be found' % ctx.unit)


@compute_vm_get_disks.command('scsi', short_help='scsi controller info')
@pass_context
def compute_vm_get_disks_scsi(ctx: Configuration):
    """Virtual disk SCSI controller info"""
    columns = ctx.columns or const.COLUMNS_VM_DISK_SCSI
    obj = ctx.get_vm_disk_scsi(ctx.uuid, ctx.unit)
    if obj:
        click.echo(format_output(ctx, [obj], columns=columns, single=True))
    else:
        logging.error('Disk %s SCSI controller could not be found' % ctx.unit)


@compute_vm_get.command('domain', short_help='Running domain')
@pass_context
def compute_vm_get_domain(ctx: Configuration):
    """Virtual machine running domain"""
    obj = ctx.get_vm_domain(ctx.uuid)
    columns = ctx.columns or [
        ('MOREF', 'domain.moref'),
        ('NAME', 'domain.name'),
    ]
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('event', short_help='Events')
@click.option('-w', '--window', type=int, default=1, help='Time window')
@pass_context
def compute_vm_get_events(ctx: Configuration, window):
    """Get virtual machine related events in given time window"""
    obj = ctx.request(f'/vm/{ctx.uuid}/event', params=dict(hours=window))
    obj = obj.get('data')
    columns = ctx.columns or const.COLUMNS_VM_EVENT
    click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('extra-cfg', short_help='GuestInfo extra configs')
@pass_context
def compute_vm_get_extra_config(ctx: Configuration):
    """Get virtual machine guest info via VMware Tools."""
    objs = ctx.get_vm_extra_cfg_options(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_EXTRA_CONFIG
    click.echo(format_output(ctx, objs, columns=columns))


@compute_vm_get.command('floppy', short_help='Floppy configuration')
@click.argument('unit', type=int, required=False)
@pass_context
def compute_vm_get_floppies(ctx: Configuration, unit):
    """Virtual machine Floppy configuration."""
    if unit:
        obj = ctx.get_vm_floppy(ctx.uuid, unit)
        if obj:
            columns = ctx.columns or const.COLUMNS_VM_CD
            click.echo(format_output(ctx, obj, columns=columns, single=True))
        else:
            logging.error('Unit does not exist')
    else:
        devs = ctx.get_vm_floppies(ctx.uuid)
        obj = [d.get('data') for d in devs] if devs else []
        columns = ctx.columns or const.COLUMNS_VM_CD_MIN
        click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('folder', short_help='Logical folder')
@pass_context
def compute_vm_get_folder(ctx: Configuration):
    """Virtual machine logical folder."""
    obj = ctx.get_vm_folder(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_FOLDER
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.group(
    'guest', short_help='Guest summary', invoke_without_command=True
)
@pass_context
def compute_vm_get_guest(ctx: Configuration):
    """Get virtual machine guest info via VMware Tools."""
    obj = ctx.get_vm_guest(ctx.uuid)
    if click.get_current_context().invoked_subcommand is None:
        columns = ctx.columns or const.COLUMNS_VM_GUEST
        click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get_guest.command('os', short_help='Guest OS configuration')
@pass_context
def compute_vm_get_guest_os(ctx: Configuration):
    """Get virtual machine guest OS."""
    obj = ctx.get_vm_guest_os(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_VM_GUEST_OS
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get_guest.command(
    'ip', short_help='Guest IP Address configuration'
)
@pass_context
def compute_vm_get_guest_ip(ctx: Configuration):
    """Get virtual machine ip addresses via VMware Tools."""
    obj = ctx.get_vm_guest_ip(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_VM_GUEST_IP
    click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('ha-group', short_help='HA Group (Metadata)')
@pass_context
def compute_vm_get_ha_group(ctx: Configuration):
    obj = ctx.get_vm_vss_ha_group(ctx.uuid)
    if obj:
        obj = obj.get('vms', [])
    else:
        obj = []
    columns = ctx.columns or const.COLUMNS_VM_HAGROUP
    click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command(
    'inform', short_help='Informational contacts (Metadata)'
)
@pass_context
def compute_vm_get_inform(ctx: Configuration):
    """Virtual machine informational contacts. Part of the
    VSS metadata."""
    obj = ctx.get_vm_vss_inform(ctx.uuid)
    if obj:
        obj = dict(inform=obj)
    columns = ctx.columns or [('inform', 'inform.[*]')]
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('memory', short_help='Memory configuration')
@pass_context
def compute_vm_get_memory(ctx: Configuration):
    """Virtual machine memory configuration."""
    obj = ctx.get_vm_memory(str(ctx.uuid))
    columns = ctx.columns or const.COLUMNS_VM_MEMORY
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('name', short_help='Logical name')
@pass_context
def compute_vm_get_name(ctx: Configuration):
    """Virtual machine human readable name."""
    obj = ctx.get_vm_name(ctx.uuid)
    columns = ctx.columns or [('name',)]
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('nic', short_help='NIC configuration')
@click.argument('unit', type=int, required=False)
@pass_context
def compute_vm_get_nics(ctx: Configuration, unit):
    """Virtual machine network interface adapters configuration."""

    if unit:
        obj = ctx.get_vm_nic(ctx.uuid, unit)
        if obj:
            columns = ctx.columns or const.COLUMNS_VM_NIC
            click.echo(format_output(ctx, obj, columns=columns, single=True))
        else:
            logging.error('Unit does not exist')
    else:
        obj = ctx.get_vm_nics(ctx.uuid)
        obj = [d.get('data') for d in obj] if obj else []
        columns = ctx.columns or const.COLUMNS_VM_NIC_MIN
        click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('perm', short_help='Permissions')
@click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
@pass_context
def compute_vm_get_perms(ctx: Configuration, page):
    """Obtain virtual machine group or user permissions."""
    obj = ctx.get_vm_permission(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_OBJ_PERMISSION
    click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('snapshot', short_help='Snapshots')
@click.argument('snapshot_id', type=int, required=False)
@pass_context
def compute_vm_get_snapshot(ctx: Configuration, snapshot_id):
    """Virtual Machine snapshots"""
    if snapshot_id:
        obj = ctx.get_vm_snapshot(ctx.uuid, snapshot_id)
        columns = ctx.columns or const.COLUMNS_VM_SNAP
        click.echo(format_output(ctx, obj, columns=columns, single=True))
    else:
        obj = ctx.get_vm_snapshots(ctx.uuid)
        columns = ctx.columns or const.COLUMNS_VM_SNAP_MIN
        click.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command(
    'spec-api',
    short_help='Cloud API configuration specification',
    context_settings={"ignore_unknown_options": True},
)
@click.argument('spec_file', type=click.Path(), required=False)
@click.option(
    '-e', '--edit', is_flag=True, required=False, help='Edit before writing'
)
@pass_context
def compute_vm_get_spec_api(ctx: Configuration, spec_file, edit):
    """Cloud API  Virtual machine configuration specification."""
    if ctx.output in ['auto', 'table']:
        _LOGGING.warning(f'Input set to {ctx.output}. Falling back to yaml')
        ctx.output = 'yaml'
    f_name = spec_file or f'{ctx.uuid}-api-spec.{ctx.output}'
    # get obj
    obj = ctx.get_vm_spec(ctx.uuid)
    new_raw = None
    if edit:
        obj_raw = raw_format_output(
            ctx.output, obj, ctx.yaml(), highlighted=False
        )
        new_raw = click.edit(obj_raw, extension='.{}'.format(ctx.output))

    if ctx.output == 'json':
        import json

        if new_raw:
            obj = json.loads(new_raw)
        with open(f_name, 'w') as fp:
            json.dump(obj, fp=fp, indent=2, sort_keys=False)
    else:
        if new_raw:
            obj = ctx.yaml_load(new_raw)
        with open(f_name, 'w') as fp:
            ctx.yaml_dump_stream(obj, stream=fp)
    click.echo(f'Written to {f_name}')


@compute_vm_get.command(
    'spec',
    short_help='CLI configuration specification',
    context_settings={"ignore_unknown_options": True},
)
@click.argument('spec_file', type=click.Path(), required=False)
@click.option(
    '-e', '--edit', is_flag=True, required=False, help='Edit before writing'
)
@pass_context
def compute_vm_get_spec(ctx: Configuration, spec_file, edit):
    """CLI Virtual machine configuration specification."""
    if ctx.output in ['auto', 'table']:
        _LOGGING.warning(f'Input set to {ctx.output}. Falling back to yaml')
        ctx.output = 'yaml'
    f_name = spec_file or f'{ctx.uuid}-cli-spec.{ctx.output}'
    # get obj
    obj = ctx.get_vm_spec(ctx.uuid)
    file_spec = os.path.join(const.DEFAULT_DATA_PATH, 'shell.yaml')
    # proceed to load file
    with open(file_spec, 'r') as data_file:
        raw = data_file.read()
    template = ctx.yaml_load(raw)
    # obj rewritten with cli spec
    obj = ctx.get_cli_spec_from_api_spec(payload=obj, template=template)
    new_raw = None
    if edit:
        obj_raw = raw_format_output(
            ctx.output, obj, ctx.yaml(), highlighted=False
        )
        new_raw = click.edit(obj_raw, extension='.{}'.format(ctx.output))

    if ctx.output == 'json':
        import json

        if new_raw:
            obj = json.loads(new_raw)
        with open(f_name, 'w') as fp:
            json.dump(obj, fp=fp, indent=2, sort_keys=False)
    else:
        if new_raw:
            obj = ctx.yaml_load(new_raw)
        with open(f_name, 'w') as fp:
            ctx.yaml_dump_stream(obj, stream=fp)
    click.echo(f'Written to {f_name}')


@compute_vm_get.command('state', short_help='Power state')
@pass_context
def compute_vm_get_state(ctx: Configuration):
    """Virtual machine running and power state."""
    obj = ctx.get_vm_state(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_VM_STATE
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('stats', short_help='Performance statistics')
@click.argument('kind', type=click.Choice(['memory', 'io', 'cpu', 'net']))
@pass_context
def compute_vm_get_stats(ctx: Configuration, kind):
    """Get virtual machine memory, io, cpu and network
     performance statistics. Choose between: io, memory,
     cpu or net. For example:

    vss-cli compute vm get <name-or-uuid> stats memory
    """
    lookup = {
        'cpu': ctx.get_vm_performance_cpu,
        'memory': ctx.get_vm_performance_memory,
        'io': ctx.get_vm_performance_io,
        'net': ctx.get_vm_performance_net,
    }

    if not ctx.is_powered_on_vm(ctx.uuid):
        raise VssCliError('Cannot perform operation in current power state')
    obj = lookup[kind](ctx.uuid)
    columns = ctx.columns or [(i,) for i in obj.keys()]
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('template', short_help='Template configuration')
@pass_context
def compute_vm_get_template(ctx: Configuration):
    """Virtual machine template state."""
    obj = ctx.is_vm_template(ctx.uuid)
    columns = ctx.columns or [('is_template',)]
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('tools', short_help='VMware Tools Status')
@pass_context
def compute_vm_get_tools(ctx: Configuration):
    """Virtual machine VMware Tools status."""
    obj = ctx.get_vm_tools(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_VM_TOOLS
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('usage', short_help='Usage (Metadata)')
@pass_context
def compute_vm_get_usage(ctx: Configuration):
    """Get current virtual machine usage.

    Part of the VSS metadata and the name prefix (YYMMP-) is composed
    by the virtual machine usage, which is intended to specify
    whether it will be hosting a Production, Development,
    QA, or Testing system."""
    obj = ctx.get_vm_vss_usage(ctx.uuid)
    columns = ctx.columns or [('usage', 'value')]
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('version', short_help='Hardware (VMX) version')
@pass_context
def compute_vm_get_version(ctx: Configuration):
    """Get VMX hardware version"""
    obj = ctx.get_vm_version(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_VM_HW
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command(
    'vmrc-copy-paste', short_help='Get VMRC copy/paste settings status'
)
@click.option(
    '-o', '--options', is_flag=True, required=False, help='Include options'
)
@pass_context
def compute_vm_get_vmrc_copy_paste(ctx: Configuration, options):
    obj = ctx.get_vm_vmrc_copy_paste(ctx.uuid, options=options)
    columns = ctx.columns or const.COLUMNS_VMRC
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('vss-option', short_help='Get VSS Option status')
@pass_context
def compute_vm_get_vss_option(ctx: Configuration):
    """Get VSS Option status"""
    obj = ctx.get_vm_vss_options(ctx.uuid)
    columns = ctx.columns or const.COLUMNS_VSS_OPTIONS
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('vss-service', short_help='Get VSS Service')
@pass_context
def compute_vm_get_vss_service(ctx: Configuration):
    """Get VSS Service"""
    obj = ctx.get_vm_vss_service(ctx.uuid)
    columns = ctx.columns  # or const.COLUMNS_VSS_SERVICE
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm.group(
    'set',
    short_help='Set virtual machine attribute',
    invoke_without_command=True,
)
@click.argument(
    'uuid_or_name',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.virtual_machines,
)
@click.option(
    '-s',
    '--schedule',
    type=click.DateTime(formats=const.SUPPORTED_DATETIME_FORMATS),
    required=False,
    default=None,
    help='Schedule change in a given point in time based'
    ' on format YYYY-MM-DD HH:MM.',
)
@click.option(
    '-u',
    '--user-meta',
    help='User metadata in key=value format. '
    'These tags are stored in the request.',
    required=False,
    default=None,
)
@so.wait_opt
@pass_context
def compute_vm_set(
    ctx: Configuration, uuid_or_name, schedule, user_meta: str, wait: bool
):
    """Manage virtual machine attributes such as cpu,
    memory, disk, network backing, cd, etc.."""
    _vm = ctx.get_vm_by_uuid_or_name(uuid_or_name)
    ctx.uuid = _vm[0]['uuid']
    # setup payload opts
    ctx.payload_options = dict()
    ctx.user_meta = dict(to_tuples(user_meta))
    ctx.schedule = schedule
    ctx.wait = wait
    # set additional props
    if user_meta:
        ctx.payload_options['user_meta'] = ctx.user_meta
    if schedule:
        # ctx.payload_options['schedule_obj'] = ctx.schedule
        ctx.payload_options['schedule'] = ctx.schedule.strftime(
            const.DEFAULT_DATETIME_FMT
        )
    if click.get_current_context().invoked_subcommand is None:
        raise click.UsageError('Sub command is required')


@compute_vm_set.command('admin', short_help='Administrator')
@click.argument('name', type=click.STRING, required=True)
@click.argument(
    'email', type=click.STRING, required=True, callback=validate_email
)
@click.argument(
    'phone', type=click.STRING, required=True, callback=validate_phone_number
)
@pass_context
def compute_vm_set_admin(ctx: Configuration, name, email, phone):
    """Set or update virtual machine administrator in metadata.

    vss-cli compute vm set <name-or-uuid> admin "Admin Name"
    admin.email@utoronto.ca 416-666-6666
    """
    payload = dict(name=name, phone=phone, email=email, uuid=ctx.uuid)
    # add common options
    payload.update(ctx.payload_options)
    # process request
    obj = ctx.update_vm_vss_admin(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('alarm', short_help='Acknowledge or clear alarms')
@click.argument('alarm_moref', type=click.STRING, required=True)
@click.option(
    '-a',
    '--action',
    type=click.Choice(['ack', 'cl']),
    help='Action to perform',
    required=True,
)
@pass_context
def compute_vm_set_alarm(ctx: Configuration, action, alarm_moref):
    """Acknowledge or clear a given alarm. Obtain alarm moref by:

        vss-cli compute vm get <name-or-uuid> alarm

        vss-cli compute vm set <name-or-uuid> alarm <moref> --action ack

    """
    payload = dict(uuid=ctx.uuid, moref=alarm_moref)
    # add common options
    payload.update(ctx.payload_options)
    # action
    if action == 'ack':
        obj = ctx.ack_vm_alarm(**payload)
    else:
        obj = ctx.clear_vm_alarm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'boot-bios', short_help='Enable or disable Boot to BIOS'
)
@click.option(
    '--on/--off',
    is_flag=True,
    help='Enable/Disable boot to BIOS',
    default=False,
)
@pass_context
def compute_vm_set_boot_bios(ctx: Configuration, on):
    """Update virtual machine boot configuration to
    boot directly to BIOS.

    vss-cli compute vm set <name-or-uuid> boot-bios --on
    vss-cli compute vm set <name-or-uuid> boot-bios --off
    """
    payload = dict(uuid=ctx.uuid, boot_bios=on)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_boot_bios(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('boot-delay', short_help='Boot delay in milliseconds')
@click.argument('delay-in-ms', type=click.INT, required=True)
@pass_context
def compute_vm_set_boot_delay(ctx: Configuration, delay_in_ms):
    """Update virtual machine boot delay time (ms).

    vss-cli compute vm set <name-or-uuid> boot-delay 5000
    """
    payload = dict(uuid=ctx.uuid, boot_delay_ms=delay_in_ms)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_boot_delay(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('cd', short_help='CD/DVD device management')
@pass_context
def compute_vm_set_cd(ctx: Configuration):
    """Manage virtual CD/DVD devices.
     Add and update CD/DVD backing"""
    pass


@compute_vm_set_cd.command('mk', short_help='Create CD/DVD unit')
@click.option(
    '-b',
    '--backing',
    type=click.STRING,
    required=True,
    multiple=True,
    help='Update CD/DVD backing device to given ISO path or Client device.',
    autocompletion=autocompletion.isos,
)
@pass_context
def compute_vm_set_cd_mk(ctx: Configuration, backing):
    """Create virtual machine CD/DVD unit with ISO or client backing.

    vss-cli compute vm set <name-or-uuid> cd mk --backing <name-or-path-or-id>

    vss-cli compute vm set <name-or-uuid> cd mk --backing client
    """
    p_backing = []
    for b in backing:
        # get iso reference
        iso_ref = ctx.get_iso_by_name_or_path(b)
        _LOGGING.debug(f'Will create {iso_ref}')
        p_backing.append(str(iso_ref[0]['id']))
    # generate payload
    payload = dict(uuid=ctx.uuid, backings=p_backing)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_cd(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_cd.command('up', short_help='Update CD/DVD unit')
@click.argument('unit', type=click.INT, required=True)
@click.option(
    '-b',
    '--backing',
    type=click.STRING,
    required=True,
    help='Update CD/DVD backing device ' 'to given ISO path or Client device.',
    autocompletion=autocompletion.isos,
)
@pass_context
def compute_vm_set_cd_up(ctx: Configuration, unit, backing):
    """Update virtual machine CD/DVD backend to ISO or client.

    vss-cli compute vm set <name-or-uuid> cd up <unit> -b <name-or-path-or-id>

    vss-cli compute vm set <name-or-uuid> cd up <unit> -b client
    """
    # get iso reference
    iso_ref = ctx.get_iso_by_name_or_path(backing)
    _LOGGING.debug(f'Will mount {iso_ref}')
    # generate payload
    payload = dict(uuid=ctx.uuid, unit=unit, iso=iso_ref[0]['path'])
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_cd(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('client', short_help='Client (Metadata)')
@click.argument('client', type=click.STRING, required=True)
@pass_context
def compute_vm_set_client(ctx: Configuration, client):
    """Update virtual machine client/billing department.

    vss-cli compute vm set <name-or-uuid> client <New-Client>
    """
    # generate payload
    payload = dict(uuid=ctx.uuid, client=client)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_client(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('client-note', short_help='Client note (Metadata)')
@click.argument('notes', required=True)
@click.option(
    '--replace',
    '-r',
    is_flag=True,
    required=False,
    help="Whether to replace existing value.",
)
@pass_context
def compute_vm_set_client_note(ctx: Configuration, notes, replace):
    """Set or update virtual machine client notes
     in metadata.

     vss-cli compute vm set <name-or-uuid> client-note "New note"
     """
    if not replace:
        _old_notes = ctx.get_vm_notes(ctx.uuid)
        old_notes = _old_notes.get('value') or ""
        notes = "{}\n{}".format(old_notes, notes)
    # generate payload
    payload = dict(uuid=ctx.uuid, notes=notes)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_notes(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('consolidate', short_help='Disk consolidation')
@pass_context
def compute_vm_set_consolidate(ctx: Configuration):
    """Perform virtual machine disk consolidation

    vss-cli compute vm set --schedule <timestamp> <name-or-uuid> consolidate
    """
    # generate payload
    payload = dict(uuid=ctx.uuid)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.consolidate_vm_disks(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('cpu')
@pass_context
def compute_vm_set_cpu(ctx: Configuration):
    """Update virtual machine CPU count and settings
    """
    pass


@compute_vm_set_cpu.command('count', short_help='Update CPU count')
@click.argument('cpu_count', type=click.INT, required=True)
@pass_context
def compute_vm_set_cpu_count(ctx: Configuration, cpu_count):
    # generate payload
    payload = dict(uuid=ctx.uuid, number=cpu_count)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.set_vm_cpu(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_cpu.command('hot-add', short_help='Enable/disable CPU hot add')
@click.argument('status', type=click.Choice(['on', 'off']), required=True)
@pass_context
def compute_vm_set_cpu_hot_add(ctx: Configuration, status):
    lookup = {'on': True, 'off': False}
    payload = dict(uuid=ctx.uuid, hot_add=lookup[status])
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_cpu_hot_add(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('custom-spec', short_help='Custom specification')
@click.option(
    '--hostname', '-h', type=click.STRING, required=True, help='OS hostname.'
)
@click.option(
    '--domain', '-m', type=click.STRING, required=True, help='OS domain.'
)
@click.option(
    '--dns',
    '-n',
    type=click.STRING,
    multiple=True,
    required=False,
    help='DNS list.',
)
@click.option(
    '--interface',
    '-i',
    type=click.STRING,
    required=False,
    multiple=True,
    help='Interfaces to customize in json format.',
)
@pass_context
def compute_vm_set_custom_spec(
    ctx: Configuration, hostname, domain, dns, interface
):
    """Set up Guest OS customization specification.
    Virtual machine power state require is powered off."""
    if ctx.is_powered_on_vm(ctx.uuid):
        raise Exception(
            'Cannot perform operation ' 'on VM with current power state'
        )
    # temp custom_spec
    _custom_spec = dict(hostname=hostname, domain=domain)
    if dns:
        _custom_spec['dns'] = dns
    interfaces = list()
    # interfaces
    if interface:
        import json

        for iface in interface:
            validate_json_type(ctx, '', iface)
            _if = json.loads(iface)
            interfaces.append(ctx.get_custom_spec_interface(**_if))
    else:
        _LOGGING.warning('No interfaces were received from input')
    # update custom spec with interfaces
    _custom_spec.update({'interfaces': interfaces})
    # create custom_spec
    custom_spec = ctx.get_custom_spec(**_custom_spec)
    # create payload
    payload = dict(uuid=ctx.uuid, custom_spec=custom_spec)
    # add common options
    payload.update(ctx.payload_options)
    # process request
    # submit custom_spec
    obj = ctx.create_vm_custom_spec(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group(
    'extra-cfg', short_help='GuestInfo extra config entries.'
)
@pass_context
def compute_vm_set_extra_config(ctx: Configuration):
    """Manage VMware **guestinfo** interface options, which are
    available to the VM guest operating system via VMware Tools:

      vmtoolsd --cmd "info-get guestinfo.<option>"
    """
    pass


@compute_vm_set_extra_config.command(
    'mk', short_help='Create guestInfo extra config entries.'
)
@click.argument('key-value', type=click.STRING, required=True, nargs=-1)
@pass_context
def compute_vm_set_extra_config_mk(ctx: Configuration, key_value):
    """Create **guestinfo** interface extra configuration options:

    vss-cli compute vm set <name-or-uuid> extra-cfg mk key1=value2 key2=value2

    """
    # process input
    try:
        _options = to_tuples(','.join(key_value))
        options = dict(_options)
    except Exception as ex:
        _LOGGING.error(ex)
        raise click.BadArgumentUsage('Argument must be key=value strings')
    # assemble payload
    payload = dict(uuid=ctx.uuid, options=options)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_extra_cfg_options(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_extra_config.command(
    'up', short_help='Update guestInfo extra config entries.'
)
@click.argument('key-value', type=click.STRING, required=True, nargs=-1)
@click.option(
    '--check/--no-check',
    is_flag=True,
    default=False,
    help='Check if options to update exist.',
)
@pass_context
def compute_vm_set_extra_config_up(ctx: Configuration, key_value, check):
    """Update **guestinfo** interface extra configuration options:

    vss-cli compute vm set <name-or-uuid> extra-cfg up key1=value2 key2=value2

    """
    # process input
    try:
        _options = to_tuples(','.join(key_value))
        options = dict(_options)
    except Exception as ex:
        _LOGGING.error(ex)
        raise click.BadArgumentUsage('Argument must be key=value strings')
    # check if key exists
    if check:
        ex_opts = [
            i['key'].replace('guestinfo.', '')
            for i in ctx.get_vm_extra_cfg_options(ctx.uuid)
        ]
        no_opts = [k for k in options if k not in ex_opts]
        if list(no_opts):
            _LOGGING.warning(
                f'Extra config options will be ignored: {", ".join(no_opts)}'
            )
    # assemble payload
    payload = dict(uuid=ctx.uuid, options=options)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_extra_cfg_options(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_extra_config.command(
    'rm', short_help='Remove guestInfo extra config option keys.'
)
@click.argument('key', type=click.STRING, required=True, nargs=-1)
@click.option(
    '--check/--no-check',
    is_flag=True,
    default=False,
    help='Check if options to update exist.',
)
@pass_context
def compute_vm_set_extra_config_rm(ctx: Configuration, key, check):
    """Remove **guestinfo** interface extra configuration options:

    vss-cli compute vm set <name-or-uuid> extra-cfg rm key1 key2 keyN

    """
    # check if key exists
    if check:
        ex_opts = [
            i['key'].replace('guestinfo.', '')
            for i in ctx.get_vm_extra_cfg_options(ctx.uuid)
        ]
        no_opts = [k for k in key if k not in ex_opts]
        if list(no_opts):
            _LOGGING.warning(
                f'Extra config options will be ignored: {", ".join(no_opts)}'
            )
    # assemble payload
    payload = dict(uuid=ctx.uuid, options=key)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.delete_vm_extra_cfg_options(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('description', short_help='Description (Metadata)')
@click.argument('description', required=True)
@pass_context
def compute_vm_set_description(ctx: Configuration, description):
    """Set or update virtual machine description in metadata.

    vss-cli compute vm set <name-or-uuid> description "new description"
    """
    payload = dict(uuid=ctx.uuid, description=description)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_description(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('disk', short_help='Disk management')
@pass_context
def compute_vm_set_disk(ctx: Configuration):
    """Manage virtual machine disks.
     Add, expand and remove virtual disks."""
    pass


@compute_vm_set_disk.command('mk', short_help='Create disk(s)')
@click.option(
    '-c',
    '--capacity',
    type=click.INT,
    required=True,
    multiple=True,
    help='Create given disk(s) capacity in GB.',
)
@pass_context
def compute_vm_set_disk_mk(ctx: Configuration, capacity):
    """Create virtual machine disk:

        vss-cli compute vm set <name-or-uuid> disk mk -c 10 -c 40
    """
    payload = dict(uuid=ctx.uuid, values_in_gb=capacity)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_disk(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_disk.command('up', short_help='Update disk capacity')
@click.argument('unit', type=click.INT, required=True)
@click.option(
    '-c',
    '--capacity',
    type=click.INT,
    required=False,
    help='Update disk capacity in GB.',
)
@click.option(
    '-s',
    '--scsi',
    type=click.INT,
    required=False,
    help='Update disk SCSI adapter',
)
@click.option(
    '-m',
    '--backing-mode',
    autocompletion=autocompletion.vm_disk_backing_modes,
    help='Update disk backing mode default [persistent]',
)
@pass_context
def compute_vm_set_disk_up(
    ctx: Configuration, unit, capacity, scsi, backing_mode
):
    """Update virtual machine disk capacity:

        vss-cli compute vm set <name-or-uuid> disk up --capacity 30 <unit>

        vss-cli compute vm set <name-or-uuid> disk up --scsi=<bus> <unit>
    """
    payload = dict(uuid=ctx.uuid, disk=unit)
    # add common options
    payload.update(ctx.payload_options)
    if capacity:
        payload['valueGB'] = capacity
        # request
        obj = ctx.update_vm_disk_capacity(**payload)
    elif scsi is not None:
        payload['bus_number'] = scsi
        obj = ctx.update_vm_disk_scsi(**payload)
    elif backing_mode is not None:
        payload['mode'] = backing_mode
        obj = ctx.update_vm_disk_backing_mode(**payload)
    else:
        raise click.BadOptionUsage(
            '', 'Either -c/--capacity or -s/--scsi is required.'
        )
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_disk.command('rm', short_help='Remove disk from vm')
@click.argument('unit', type=click.INT, required=True, nargs=-1)
@click.option(
    '-r', '--rm', is_flag=True, default=False, help='Confirm disk removal'
)
@pass_context
def compute_vm_set_disk_rm(ctx: Configuration, unit, rm):
    """Remove virtual machine disks. Warning: data will be lost:

        vss-cli compute vm set <name-or-uuid> disk rm <unit> <unit> ...
    """
    payload = dict(uuid=ctx.uuid, units=list(unit))
    # add common options
    payload.update(ctx.payload_options)
    # confirm
    confirm = rm or click.confirm(
        f'Are you sure you want to delete disk unit {unit}?'
    )
    if confirm:
        obj = ctx.delete_vm_disks(**payload)
    else:
        raise click.ClickException('Cancelled by user.')
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('domain', short_help='Domain migration')
@click.argument(
    'domain_moref',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.domains,
)
@click.option(
    '-f',
    '--force',
    is_flag=True,
    help='Shut down or power off before migration.',
)
@click.option('-o', '--on', is_flag=True, help='Power of after migrating')
@pass_context
def compute_vm_set_domain(ctx: Configuration, domain_moref, force, on):
    """Migrate a virtual machine to another fault domain.
    In order to proceed with the virtual machine relocation,
    it's required to be in a powered off state. The `force` flag
    will send a shutdown signal anf if times out, will perform a
    power off task. After migration completes, the `on` flag
    indicates to power on the virtual machine.

    vss-cli compute vm set <name-or-uuid> domain <domain-moref> --force --on
    """
    payload = dict(uuid=ctx.uuid, moref=domain_moref, poweron=on, force=force)
    if not ctx.get_domain(domain_moref):
        raise click.BadArgumentUsage(f'Domain {domain_moref} does not exist')
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_domain(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('export', short_help='Export to OVF')
@pass_context
def compute_vm_set_export(ctx: Configuration):
    """Export current virtual machine to OVF.

    vss-cli compute vm set <name-or-uuid> export
    """
    payload = dict(uuid=ctx.uuid)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.export_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('floppy', short_help='Floppy backing')
@click.argument('unit', type=click.INT, required=True)
@click.option(
    '-i',
    '--image',
    type=click.STRING,
    required=False,
    default='client',
    help='Update floppy backing device to given flp image path.',
    autocompletion=autocompletion.floppies,
)
@pass_context
def compute_vm_set_floppy(ctx: Configuration, unit, image):
    """Update virtual machine floppy backend to Image or client"""
    img_ref = ctx.get_floppy_by_name_or_path(image)
    _LOGGING.debug(f'Will mount {img_ref}')
    image = img_ref[0].get('path')
    # generate payload
    payload = dict(uuid=ctx.uuid, unit=unit, image=image)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_floppy(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('folder', short_help='Logical folder')
@click.argument(
    'name-moref-path',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.folders,
)
@pass_context
def compute_vm_set_folder(ctx: Configuration, name_moref_path):
    """Move vm from logical folder. Get folder moref from:

        vss-cli compute folder ls

    """
    # create payload
    payload = dict(uuid=ctx.uuid)
    # lookup for folder
    _folder = ctx.get_folder_by_name_or_moref_path(name_moref_path)
    payload['folder_moId'] = _folder[0]['moref']
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_folder(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('guest-cmd', short_help='Execute command on OS host')
@click.option(
    '-u',
    '--username',
    help='Guest Operating System username or via '
    'environment variable VSS_CMD_USER',
    envvar='VSS_CMD_USER',
)
@click.option(
    '-p',
    '--password',
    help='Guest Operating System username password or via '
    'environment variable VSS_CMD_USER_PASS',
    envvar='VSS_CMD_USER_PASS',
)
@click.option(
    '-e',
    '--env',
    multiple=True,
    help='Environment variables in KEY=value format.',
)
@click.argument('cmd', type=click.STRING, required=True)
@click.argument('cmd-args', type=click.STRING, required=True)
@pass_context
def compute_vm_set_guest_cmd(ctx, cmd, cmd_args, env, username, password):
    """
    Execute a command in the Guest Operating system.

    vss-cli compute vm set <name-or-uuid> guest-cmd "/bin/echo"
    "Hello > /tmp/hello.txt"

    Note: VMware Tools must be installed and running.
    """
    username = username or click.prompt('Username')
    password = password or click.prompt(
        'Password',
        show_default=False,
        hide_input=True,
        confirmation_prompt=True,
    )
    # check vmware tools status
    vmt = ctx.get_vm_tools(ctx.uuid)
    if not vmt:
        raise click.BadParameter(
            f'VMware Tools status could ' f'not be checked on {ctx.uuid} '
        )
    if vmt.get('runningStatus') not in ["guestToolsRunning"]:
        raise click.BadParameter(
            f'VMware Tools must be running ' f'on {ctx.uuid} to execute cmd.'
        )
    # creating payload
    payload = dict(
        uuid=ctx.uuid,
        user=username,
        pwd=password,
        cmd=cmd,
        arg=cmd_args,
        env=env,
    )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.run_cmd_guest_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('guest-os', short_help='Update guest operating system')
@click.argument(
    'guest-id',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.operating_systems,
)
@pass_context
def compute_vm_set_guest_os(ctx: Configuration, guest_id):
    """Update guest operating system configuration:

        vss-cli compute vm set <name-or-uuid> guest-os <name-or-name>

    """
    g_os = ctx.get_os_by_name_or_guest(guest_id)
    g_id = g_os[0]['guest_id']
    # create payload
    payload = dict(uuid=ctx.uuid, os=g_id)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_os(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('ha-group', short_help='HA Group (Metadata)')
@click.argument('uuid', type=click.UUID, nargs=-1, required=True)
@click.option(
    '-r',
    '--replace',
    is_flag=True,
    required=False,
    help='Replace existing value.',
)
@pass_context
def compute_vm_set_ha_group(ctx: Configuration, uuid, replace):
    """Create HA group by tagging virtual machines with given
    virtual machine UUIDs.

    Checks will run every 3 hours to validate virtual machine
    association and domain separation.

    vss-cli compute vm set <name-or-uuid> ha-group --replace <uuid-1> <uuid-n>
    """
    for vm in uuid:
        _vm = ctx.get_vm(vm)
        if not _vm:
            raise click.BadArgumentUsage(f'{vm} could not be found')
    # create payload
    payload = dict(
        append=not replace, vms=list(map(str, uuid)), uuid=str(ctx.uuid)
    )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_ha_group(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'inform', short_help='Informational contacts (Metadata)'
)
@click.argument('email', type=click.STRING, nargs=-1, required=True)
@click.option(
    '-r',
    '--replace',
    is_flag=True,
    required=False,
    help='Replace existing value.',
)
@pass_context
def compute_vm_set_inform(ctx: Configuration, email, replace):
    """Update or set informational contacts emails in
    metadata.

    vss-cli compute vm set <name-or-uuid> inform <email-1> <email-n>
    """
    for e in email:
        validate_email(ctx, '', e)
    # create payload
    payload = dict(append=not replace, emails=list(email), uuid=ctx.uuid)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_inform(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('memory')
@pass_context
def compute_vm_set_memory(ctx: Configuration):
    """Update virtual machine Memory count and settings
    """
    pass


@compute_vm_set_memory.command('size', short_help='Update memory size in GB')
@click.argument('memory_gb', type=click.INT, required=True)
@pass_context
def compute_vm_set_memory_size(ctx: Configuration, memory_gb):
    """Update virtual machine memory size in GB.

    vss-cli compute vm set <name-or-uuid> memory size <memory_gb>

    """
    # create payload
    payload = dict(sizeGB=memory_gb, uuid=ctx.uuid)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.set_vm_memory(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_memory.command(
    'hot-add', short_help='Enable/disable Memory hot add'
)
@click.argument('status', type=click.Choice(['on', 'off']), required=True)
@pass_context
def compute_vm_set_memory_hot_add(ctx: Configuration, status):
    """Enable or disable virtual machine memory hot-add setting

    vss-cli compute vm set <name-or-uuid> memory hot-add on|off

    """
    lookup = {'on': True, 'off': False}
    # create payload
    payload = dict(uuid=ctx.uuid, hot_add=lookup[status])
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_memory_hot_add(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('name', short_help='Logical name')
@click.argument('name', type=click.STRING, required=True)
@pass_context
def compute_vm_set_name(ctx: Configuration, name):
    """Update virtual machine name only. It does not update
    VSS prefix YYMM{P|D|Q|T}.

    vss-cli compute vm set <name-or-uuid> name <new-name>

    """
    payload = dict(name=name, uuid=ctx.uuid)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.rename_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('nic', short_help='Network adapter management')
@pass_context
def compute_vm_set_nic(ctx: Configuration):
    """Add, remove or update virtual machine network adapters

    """
    pass


@compute_vm_set_nic.command('up', short_help='Update NIC unit')
@click.argument('unit', type=click.INT, required=True)
@click.option(
    '-n',
    '--network',
    type=click.STRING,
    help='Virtual network moref',
    autocompletion=autocompletion.networks,
)
@click.option(
    '-s',
    '--state',
    type=click.Choice(['connect', 'disconnect']),
    help='Updates nic state',
)
@click.option(
    '-a',
    '--adapter',
    type=click.STRING,
    help='Updates nic adapter type',
    autocompletion=autocompletion.virtual_nic_types,
)
@pass_context
def compute_vm_set_nic_up(ctx: Configuration, unit, network, state, adapter):
    """Update network adapter backing network, type or state

        vss-cli compute vm set <name-or-uuid> nic up <unit> --adapter <type>


        vss-cli compute vm set <name-or-uuid> nic up <unit> --network <network>
    """
    # create payload
    payload = dict(uuid=ctx.uuid, nic=unit)
    # add common options
    payload.update(ctx.payload_options)
    # process request
    lookup = {
        'network': ctx.update_vm_nic_network,
        'state': ctx.update_vm_nic_state,
        'type': ctx.update_vm_nic_type,
    }
    # select attr
    if network:
        # search by name or moref
        net = ctx.get_network_by_name_or_moref(network)
        attr = 'network'
        value = net[0]['moref']
    elif state:
        attr = 'state'
        value = state
    elif adapter:
        n_type = ctx.get_vm_nic_type_by_name(adapter)
        attr = 'type'
        value = n_type[0]['type']
    else:
        raise click.UsageError('Select at least one setting to change')
    _LOGGING.debug(f'Update NIC {unit} {attr} to {value}')
    # lookup function to call
    f = lookup[attr]
    payload[attr] = value
    # request
    obj = f(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_nic.command('mk', short_help='Create NIC unit')
@c_so.networks_opt
@pass_context
def compute_vm_set_nic_mk(ctx: Configuration, net):
    """Add network adapter specifying backing network and adapter type.

        vss-cli compute vm set <name-or-uuid> nic mk
        -n <moref-or-name>=<nic-type> -n <moref-or-name>
    """
    # create payload
    payload = dict(uuid=ctx.uuid)
    # add common options
    payload.update(ctx.payload_options)
    # payload
    payload['networks'] = net
    # request
    obj = ctx.create_vm_nic(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_nic.command('rm', short_help='Remove NIC unit')
@click.argument('unit', type=click.INT, required=True, nargs=-1)
@click.option(
    '-c', '--confirm', is_flag=True, default=False, help='Confirm nic removal'
)
@pass_context
def compute_vm_set_nic_rm(ctx: Configuration, unit, confirm):
    """Remove given network adapters

        vss-cli compute vm set <name-or-uuid> nic rm <unit> <unit> ...
    """
    # create payload
    payload = dict(uuid=ctx.uuid)
    units_payload = []
    # add common options
    payload.update(ctx.payload_options)
    confirm_message = list()
    # validate adapters
    for n in unit:
        _nic = ctx.get_vm_nic(uuid=ctx.uuid, nic=n)
        if _nic:
            _nic = _nic.pop()
            _message = const.DEFAULT_NIC_DEL_MSG.format(**_nic)
            confirm_message.append(_message)
            units_payload.append(n)
        else:
            _LOGGING.warning(f'Adapter {n} could not be found. Ignoring.')
    if not units_payload:
        raise click.BadArgumentUsage('No valid adapters could be found.')
    else:
        payload['units'] = units_payload
    confirm_message.append(
        'Are you sure you want to delete the following NICs'
    )
    confirm_message_str = '\n'.join(confirm_message)
    # confirm message
    confirm = confirm or click.confirm(confirm_message_str)
    # request
    if confirm:
        obj = ctx.delete_vm_nics(**payload)
    else:
        raise click.ClickException('Cancelled by user.')
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('snapshot', short_help='Snapshot management')
@pass_context
def compute_vm_set_snapshot(ctx: Configuration):
    """Manage virtual machine snapshots. Create, delete and revert
    virtual machine snapshot on a given date and time."""
    if ctx.payload_options.get('schedule'):
        _LOGGING.warning('schedule is ignored for snapshots. Removing.')
        del ctx.payload_options['schedule']


@compute_vm_set_snapshot.command('mk', short_help='Create snapshot')
@click.option(
    '-d',
    '--description',
    type=click.STRING,
    required=True,
    help='A brief description of the snapshot.',
)
@click.option(
    '-t',
    '--timestamp',
    type=click.DateTime(formats=[const.DEFAULT_DATETIME_FMT]),
    default=datetime.datetime.strftime(
        datetime.datetime.now(), const.DEFAULT_DATETIME_FMT
    ),
    required=False,
    show_default=True,
    help='Timestamp to create the snapshot from.',
)
@click.option(
    '-l',
    '--lifetime',
    type=click.IntRange(1, 72),
    default=24,
    required=False,
    show_default=True,
    help='Number of hours the snapshot will live.',
)
@pass_context
def compute_vm_set_snapshot_mk(
    ctx: Configuration, description, timestamp, lifetime
):
    """Create virtual machine snapshot:

       vss-cli compute vm set <name-or-uuid> snapshot mk -d 'Short description'

       Note: if -t/--timestamp not specified, the snapshot request timestamp
       is current time.
    """

    # create payload
    payload = dict(
        uuid=ctx.uuid,
        desc=description,
        date_time=datetime.datetime.strftime(
            timestamp, const.DEFAULT_DATETIME_FMT
        ),
        valid=lifetime,
    )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_snapshot(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_snapshot.command('rm', short_help='Remove snapshot')
@click.argument('snapshot_id', type=click.INT, required=True)
@pass_context
def compute_vm_set_snapshot_rm(ctx: Configuration, snapshot_id):
    """Remove virtual machine snapshot:

        vss-cli compute vm set <name-or-uuid> snapshot rm <snapshot-id>
    """
    # create payload
    payload = dict(uuid=ctx.uuid, snapshot=snapshot_id)
    if not ctx.get_vm_snapshot(uuid=ctx.uuid, snapshot=snapshot_id):
        raise click.BadArgumentUsage(
            f'Snapshot ID {snapshot_id} could not be found.'
        )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.delete_vm_snapshot(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_snapshot.command('re', short_help='Revert snapshot')
@click.argument('snapshot_id', type=click.INT, required=True)
@pass_context
def compute_vm_set_snapshot_re(ctx: Configuration, snapshot_id):
    """Revert virtual machine snapshot:

        vss-cli compute vm set <name-or-uuid> snapshot re <snapshot-id>
    """
    # create payload
    payload = dict(uuid=ctx.uuid, snapshot=snapshot_id)
    if not ctx.get_vm_snapshot(uuid=ctx.uuid, snapshot=snapshot_id):
        raise click.BadArgumentUsage(
            f'Snapshot ID {snapshot_id} could not be found.'
        )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.revert_vm_snapshot(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('state', short_help='Power state')
@click.argument(
    'state',
    type=click.Choice(['on', 'off', 'reboot', 'reset', 'shutdown']),
    required=True,
)
@click.option(
    '-c', '--confirm', is_flag=True, default=False, help='Confirm state change'
)
@pass_context
def compute_vm_set_state(ctx: Configuration, state, confirm):
    """ Set given virtual machine power state.

    vss-cli compute vm set <name-or-uuid> state on|off|reset|reboot|shutdown -c

    Reboot and shutdown send a guest OS restart signal
    (VMware Tools required).

    """
    # lookup dict for state
    lookup = {
        'on': 'poweredOn',
        'off': 'poweredOff',
        'reset': 'reset',
        'reboot': 'reboot',
        'shutdown': 'shutdown',
    }
    # create payload
    payload = dict(uuid=ctx.uuid, state=lookup[state])
    # add common options
    payload.update(ctx.payload_options)
    # validate VMware tools if shutdown/reboot
    if state in ['reboot', 'shutdown']:
        vmt = ctx.get_vm_tools(ctx.uuid)
        if not vmt:
            raise click.BadParameter(
                f'VMware Tools status could ' f'not be checked on {ctx.uuid} '
            )
        if vmt.get('runningStatus') not in ["guestToolsRunning"]:
            raise click.BadParameter(
                f'VMware Tools must be running '
                f'on {ctx.uuid} send a reboot or shutdown '
                f'signal.'
            )
    # process request
    # show guest os info if no confirmation flag has been
    # included - just checking
    guest_info = ctx.get_vm_guest(ctx.uuid)
    ip_addresses = (
        ', '.join(guest_info.get('ip_address'))
        if guest_info.get('ip_address')
        else ''
    )
    # confirmation string
    confirmation_str = const.DEFAULT_STATE_MSG.format(
        state=state, ip_addresses=ip_addresses, **guest_info
    )
    confirmation = confirm or click.confirm(confirmation_str)
    if not confirmation:
        raise click.ClickException('Cancelled by user.')
    # request
    obj = ctx.update_vm_state(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'template', short_help='Mark vm as template or vice versa.'
)
@click.option(
    '--on/--off',
    is_flag=True,
    help='Marks vm as template or template as vm',
    default=False,
)
@pass_context
def compute_vm_set_template(ctx: Configuration, on):
    """Marks virtual machine as template or template to virtual machine.

    vss-cli compute vm set <name-or-uuid> template --on/--off
    """
    # create payload
    payload = dict(uuid=ctx.uuid, value=on)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.mark_template_as_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('tools', short_help='Manage VMware Tools')
@click.argument(
    'action', type=click.Choice(['upgrade', 'mount', 'unmount']), required=True
)
@pass_context
def compute_vm_set_tools(ctx: Configuration, action):
    """Upgrade, mount and unmount official VMware Tools package.
    This command does not apply for Open-VM-Tools.

    vss-cli compute vm set <name-or-uuid> tools upgrade|mount|unmount
    """
    payload = dict(uuid=ctx.uuid, action=action)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_tools(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('usage', short_help='Usage (Metadata)')
@click.argument(
    'usage', type=click.Choice(['Prod', 'Test', 'Dev', 'QA']), required=True
)
@pass_context
def compute_vm_set_usage(ctx: Configuration, usage):
    """Update virtual machine usage in both name prefix
    and metadata.

    vss-cli compute vm set <name-or-uuid> usage Prod|Test|Dev|QA
    """
    # create payload
    payload = dict(uuid=ctx.uuid, usage=usage)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_usage(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('version')
@pass_context
def compute_vm_set_version(ctx: Configuration):
    """Manage virtual machine virtual hardware version and policy."""


@compute_vm_set_version.command(
    'vmx', short_help='Update hardware (VMX) version'
)
@click.argument(
    'vmx',
    type=click.Choice(['vmx-11', 'vmx-12', 'vmx-13']),
    required=False,
    default='vmx-13',
)
@pass_context
def compute_vm_set_version_policy_vmx(ctx: Configuration, vmx):
    """Update virtual hardware version."""
    # create payload
    payload = dict(uuid=ctx.uuid, vmx=vmx)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_version(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_version.command(
    'policy', short_help='Update hardware (VMX) version ' 'upgrade policy'
)
@click.argument(
    'policy',
    type=click.Choice(['never', 'onSoftPowerOff', 'always']),
    required=True,
)
@pass_context
def compute_vm_set_version_policy(ctx: Configuration, policy):
    """Update virtual hardware version upgrade policy."""
    # create payload
    payload = dict(uuid=ctx.uuid, policy=policy)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_version_policy(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'vmrc-copy-paste', short_help='Enable or disable VMRC copy-paste settings'
)
@click.option(
    '--on/--off',
    help='Enable or disable VMRC copy-paste settings',
    default=None,
)
@pass_context
def compute_vm_set_vmrc_copy_paste(ctx: Configuration, on):
    """Enable or disable copy/paste between VMRC and VM OS"""
    # create payload
    payload = dict(uuid=ctx.uuid)
    # add common options
    payload.update(ctx.payload_options)
    # request
    if on:
        obj = ctx.enable_vm_vmrc_copy_paste(**payload)
    else:
        obj = ctx.disable_vm_vmrc_copy_paste(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'vss-option', short_help='Enable or disable given vss-option'
)
@click.argument(
    'vss-option', type=click.Choice(['reboot_on_restore', 'reset_on_restore'])
)
@click.option(
    '--on/--off', help='Enable or disable given vss-option', default=False
)
@pass_context
def compute_vm_set_vss_option(ctx: Configuration, vss_option, on):
    """Enable or disable given VSS Option"""
    # create payload
    payload = dict(uuid=ctx.uuid, option_name=vss_option)
    # add common options
    payload.update(ctx.payload_options)
    # request
    if on:
        obj = ctx.enable_vm_vss_option(**payload)
    else:
        obj = ctx.disable_vm_vss_option(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('vss-service', short_help='VSS Service name or ID')
@click.argument(
    'label-name-or-id',
    autocompletion=autocompletion.vss_services,
    type=click.STRING,
    required=True,
)
@pass_context
def compute_vm_set_vss_service(ctx: Configuration, label_name_or_id):
    """Update VSS service name or ID"""
    service = ctx.get_vss_service_by_name_label_or_id(label_name_or_id)[0][
        'id'
    ]
    # create payload
    payload = dict(uuid=ctx.uuid, service_name_or_id=service)
    # add common options
    payload.update(ctx.payload_options)
    obj = ctx.update_vm_vss_service(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group(
    'controller', short_help='IDE/SCSI controller management'
)
@pass_context
def compute_vm_set_controller(ctx: Configuration):
    """Manage virtual machine IDE/SCSI controllers.
     Add, update and remove controllers."""
    pass


@compute_vm_set_controller.group(
    'scsi', short_help='SCSI controller management'
)
@pass_context
def compute_vm_set_controller_scsi(ctx: Configuration):
    """Manage virtual machine SCSI controllers.
     Add, update and remove controllers."""
    pass


@compute_vm_set_controller_scsi.command(
    'mk', short_help='Create SCSI controller(s)'
)
@click.option(
    '-t',
    '--scsi-type',
    required=True,
    multiple=True,
    autocompletion=autocompletion.vm_controller_scsi_types,
    default='paravirtual',
    help='Type of SCSI Controllers.',
    show_default=True,
)
@pass_context
def compute_vm_set_controller_scsi_mk(ctx: Configuration, scsi_type):
    """Create virtual machine SCSI controllers:

        vss-cli compute vm set <name-or-uuid> controller scsi mk
        -t paravirtual -t lsilogic
    """
    payload = dict(uuid=ctx.uuid, types=scsi_type)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_scsi_device(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_controller_scsi.command(
    'up', short_help='Update SCSI controller'
)
@click.argument('bus_number', type=click.INT, required=True)
@click.option(
    '-t',
    '--scsi-type',
    autocompletion=autocompletion.vm_controller_scsi_types,
    required=True,
    help='Type of SCSI Controllers.',
)
@pass_context
def compute_vm_set_controller_scsi_up(
    ctx: Configuration, bus_number, scsi_type
):
    """Update virtual machine SCSI controller type:

        vss-cli compute vm set <name-or-uuid> controller scsi up
        <bus> -t paravirtual

    """
    # validate if unit exists
    bus = ctx.get_vm_scsi_device(ctx.uuid, bus_number)
    if not bus:
        raise click.BadOptionUsage('', 'SCSI bus could not be found.')
    payload = dict(uuid=ctx.uuid, bus=bus_number, bus_type=scsi_type)
    # add common options
    payload.update(ctx.payload_options)
    obj = ctx.update_vm_scsi_device_type(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_set_controller_scsi.command(
    'rm', short_help='Remove SCSI controller(s)'
)
@click.argument('bus_number', type=click.INT, required=True, nargs=-1)
@click.option(
    '-r',
    '--rm',
    is_flag=True,
    default=False,
    help='Confirm controller removal',
)
@pass_context
def compute_vm_set_controller_scsi_rm(ctx: Configuration, bus_number, rm):
    """Remove virtual machine SCSI controllers.

        vss-cli compute vm set <name-or-uuid> controller scsi rm <bus> ...
    """
    buses = list(bus_number)
    for bus in buses:
        # TODO: remove when get_vm_scsi_device is fixed
        _bus = ctx.request('/vm/%s/controller/scsi/%s' % (ctx.uuid, bus))
        if not _bus.get('data'):
            buses.remove(bus)
            _LOGGING.warning(
                f'Ignoring SCSI Controller {bus}. ' f'Could not be found.'
            )
        else:
            devices = ctx.get_vm_disk_by_scsi_device(ctx.uuid, bus)
            if devices:
                buses.remove(bus)
                _LOGGING.warning(
                    f'Ignoring SCSI Controller {bus}. '
                    f'Device has {len(devices)} disk(s) attached.'
                )
    if not buses:
        raise click.BadArgumentUsage(
            'No valid SCSI Controllers could be found'
        )
    payload = dict(uuid=ctx.uuid, buses=buses)
    # add common options
    payload.update(ctx.payload_options)
    # confirm
    confirm = rm or click.confirm(
        f'Are you sure you want to SCSI bus {buses}?'
    )
    if confirm:
        obj = ctx.delete_vm_scsi_devices(**payload)
    else:
        raise click.ClickException('Cancelled by user.')
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm.group(
    'rm', help='Delete given virtual machines', invoke_without_command=True
)
@click.option(
    '-f',
    '--force',
    is_flag=True,
    default=False,
    help='Force deletion if power state is on',
)
@click.option(
    '-m', '--max-del', type=click.IntRange(1, 10), required=False, default=3
)
@click.option(
    '-s',
    '--show-info',
    is_flag=True,
    default=False,
    help='Show guest info and confirmation ' 'if -f/--force is not included.',
)
@click.argument(
    'uuid',
    type=click.UUID,
    required=True,
    nargs=-1,
    autocompletion=autocompletion.networks,
)
@pass_context
def compute_vm_rm(ctx: Configuration, uuid, force, max_del, show_info):
    """ Delete a list of virtual machine uuids:

        vss-cli compute vm rm <name-or-uuid> <name-or-uuid> --show-info

    """
    # result set
    objs = list()
    if len(uuid) > max_del:
        raise click.BadArgumentUsage(
            'Increase max instance removal with ' '--max-del/-m option'
        )
    #
    for vm in uuid:
        skip = False
        _vm = ctx.get_vm(vm)
        if not _vm:
            _LOGGING.warning(
                f'Virtual machine {vm} could not be found. ' f'Skipping.'
            )
            skip = True
        if _vm and show_info:
            folder_info = ctx.get_vm_folder(vm)
            name = ctx.get_vm_name(vm)
            guest_info = ctx.get_vm_guest(vm)
            ip_addresses = (
                ', '.join(guest_info.get('ip_address'))
                if guest_info.get('ip_address')
                else ''
            )

            c_str = const.DEFAULT_VM_DEL_MSG.format(
                name=name,
                folder_info=folder_info,
                ip_addresses=ip_addresses,
                **guest_info,
            )
            confirmation = force or click.confirm(c_str)
            if not confirmation:
                _LOGGING.warning(f'Skipping {vm}...')
                skip = True
        if not skip:
            # request
            payload = dict(uuid=vm, force=force)
            objs.append(ctx.delete_vm(**payload))
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    for obj in objs:
        click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm.group(
    'mk', short_help='Create virtual machine', invoke_without_command=True
)
@click.option(
    '-u',
    '--user-meta',
    help='User metadata in key=value format. '
    'These tags are stored in the request.',
    required=False,
    default=None,
)
@so.wait_opt
@pass_context
def compute_vm_mk(ctx: Configuration, user_meta: str, wait: bool):
    """Manage virtual machine attributes such as cpu,
    memory, disk, network backing, cd, etc.."""
    ctx.payload_options = dict()
    ctx.user_meta = dict(to_tuples(user_meta))
    ctx.wait = wait
    if user_meta:
        ctx.payload_options['user_meta'] = ctx.user_meta
    if click.get_current_context().invoked_subcommand is None:
        raise click.UsageError('Sub command is required')


@compute_vm_mk.command(
    'from-file',
    short_help='Create virtual machine from VSS CLI specification.',
)
@click.argument('file-spec', type=click.File('r'), required=False)
@click.option(
    '-t',
    '--spec-template',
    required=False,
    type=click.Choice(['shell']),
    help='Specification template to load and edit.',
)
@click.option(
    '-e',
    '--edit',
    is_flag=True,
    required=False,
    help='Edit before submitting request',
)
@click.option(
    '--save',
    '-s',
    default=False,
    is_flag=True,
    help='Save file after editing.',
)
@pass_context
def compute_vm_from_file(
    ctx: Configuration, file_spec, edit, spec_template, save
):
    """Create virtual machine from VSS CLI file specification.

    Run the following command to deploy a vm based on a
    VSS CLI specification template:

        vss-cli compute vm mk from-file -s -t shell -e vm.yaml

    Or from an existing vm:

        vss-cli compute vm get <vm_name_or_uuid> spec --edit vm.yaml

    Edit vm.yaml file and deploy as follows:

        vss-cli compute vm mk from-file <cli-spec>.json|yaml

    """
    import time
    from pick import pick

    if file_spec:
        raw = file_spec.read()
    else:
        # load default configuration
        if not spec_template:
            message = (
                'Please choose a template to load '
                '(press SPACE to mark, ENTER to continue): '
            )
            spec_template, index = pick(['shell'], message)
        file_spec = os.path.join(
            const.DEFAULT_DATA_PATH, f'{spec_template}.yaml'
        )
        # proceed to load file
        with open(file_spec, 'r') as data_file:
            raw = data_file.read()
    # whether to launch the editor and save file
    # before submitting request
    if edit:
        # launch editor
        new_raw = click.edit(raw, extension='.yaml')
        # load object
        if new_raw and save:
            new_obj = ctx.yaml_load(new_raw)
            file_name = f'from-file-{int(time.time())}.yaml'
            _LOGGING.debug(f'Saving spec to {file_name}')
            with open(file_name, 'w') as fp:
                ctx.yaml_dump_stream(new_obj, stream=fp)
            raw = new_raw
        else:
            _LOGGING.warning('Editor contents will not be saved.')

    payload = ctx.yaml_load(raw)
    _LOGGING.debug(f'Payload from raw: f{payload}')
    # add common options
    spec_payload = dict()
    spec_payload.update(ctx.payload_options)
    if payload['built'] == 'os_install':
        spec_payload = ctx.get_api_spec_from_cli_spec(
            payload=payload, built='os_install'
        )
    else:
        raise click.UsageError('Not yet implemented. ')
    # request
    obj = ctx.create_vm(**spec_payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_vm_mk.command(
    'from-spec', short_help='Create vm from another vm spec'
)
@c_so.source_opt
@c_so.description_opt
@c_so.bill_dept_nr_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_nr_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.folder_nr_opt
@c_so.disks_nr_opt
@c_so.networks_nr_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.iso_opt
@c_so.extra_config_opt
@c_so.vss_service_opt
@c_so.instances
@click.argument('name', type=click.STRING, required=True)
@pass_context
def compute_vm_mk_spec(
    ctx: Configuration,
    name,
    source,
    description,
    bill_dept,
    usage,
    memory,
    cpu,
    folder,
    disk,
    notes,
    admin,
    inform,
    iso,
    net,
    domain,
    os,
    extra_config,
    vss_service,
    instances,
):
    """Create virtual machine based on another virtual machine
     configuration specification. This command takes the vm
     machine specification (memory, disk, networking, etc) as a
     base for a new VM."""
    built = 'os_install'
    _vm = ctx.get_vm_by_uuid_or_name(source)
    vm_uuid = _vm[0]['uuid']
    s_payload = ctx.get_vm_spec(vm_uuid)
    # payload
    payload = dict(
        description=description, name=name, usage=usage, built=built
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = cpu
    if disk:
        payload['disks'] = list(disk)
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    if iso:
        _iso = ctx.get_iso_by_name_or_path(iso)
        payload['iso'] = _iso[0]['path']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if bill_dept:
        payload['bill_dept'] = bill_dept
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    # updating spec with new vm spec
    s_payload.update(payload)
    _LOGGING.debug(f'source={s_payload}')
    _LOGGING.debug(f'spec={payload}')
    payload = s_payload
    _LOGGING.debug(f'final spec={payload}')
    # request
    if instances > 1:
        payload['count'] = instances
        obj = ctx.create_vms(**payload)
        _columns = const.COLUMNS_REQUEST_MULT_SUBMITTED
    else:
        obj = ctx.create_vm(**payload)
        _columns = const.COLUMNS_REQUEST_SUBMITTED
    # print
    columns = ctx.columns or _columns
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        if instances > 1:
            ctx.wait_for_requests_to(obj)
        else:
            ctx.wait_for_request_to(obj)


@compute_vm_mk.command('shell', short_help='Create empty virtual machine')
@c_so.description_opt
@c_so.bill_dept_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.folder_opt
@c_so.disks_opt
@c_so.networks_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.iso_opt
@c_so.high_io_opt
@c_so.extra_config_opt
@c_so.vss_service_opt
@c_so.instances
@click.argument('name', type=click.STRING, required=True)
@pass_context
def compute_vm_mk_shell(
    ctx: Configuration,
    name,
    description,
    bill_dept,
    usage,
    memory,
    cpu,
    folder,
    disk,
    notes,
    admin,
    inform,
    high_io,
    iso,
    net,
    domain,
    os,
    extra_config,
    vss_service,
    instances,
):
    """Create a new virtual machine with no operating system
    pre-installed."""
    built = 'os_install'
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        built=built,
        high_io=high_io,
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = cpu
    if disk:
        payload['disks'] = list(disk)
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    if iso:
        _iso = ctx.get_iso_by_name_or_path(iso)
        payload['iso'] = _iso[0]['path']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if bill_dept:
        payload['bill_dept'] = bill_dept
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    # request
    if instances > 1:
        payload['count'] = instances
        obj = ctx.create_vms(**payload)
        _columns = const.COLUMNS_REQUEST_MULT_SUBMITTED
    else:
        obj = ctx.create_vm(**payload)
        _columns = const.COLUMNS_REQUEST_SUBMITTED
    # print
    columns = ctx.columns or _columns
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        if instances > 1:
            ctx.wait_for_requests_to(obj)
        else:
            ctx.wait_for_request_to(obj)


@compute_vm_mk.command('from-template', short_help='Create vm from template')
@c_so.source_template_opt
@c_so.description_opt
@c_so.bill_dept_nr_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_nr_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.folder_nr_opt
@c_so.disks_nr_opt
@c_so.networks_nr_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.custom_spec_opt
@c_so.extra_config_opt
@c_so.vss_service_opt
@c_so.instances
@click.argument('name', type=click.STRING, required=False)
@pass_context
def compute_vm_mk_template(
    ctx: Configuration,
    name,
    source,
    description,
    bill_dept,
    usage,
    memory,
    cpu,
    folder,
    disk,
    notes,
    admin,
    inform,
    net,
    domain,
    os,
    custom_spec,
    extra_config,
    vss_service,
    instances,
):
    """Deploy virtual machine from template"""
    # get source from uuid or name
    _vm = ctx.get_vm_by_uuid_or_name(source)
    vm_uuid = _vm[0]['uuid']
    # payload
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        source_template=vm_uuid,
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = cpu
    if disk:
        payload['disks'] = list(disk)
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if bill_dept:
        payload['bill_dept'] = bill_dept
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if custom_spec:
        payload['custom_spec'] = custom_spec
    # request
    if instances > 1:
        payload['count'] = instances
        obj = ctx.deploy_vms_from_template(**payload)
        _columns = const.COLUMNS_REQUEST_MULT_SUBMITTED
    else:
        obj = ctx.deploy_vm_from_template(**payload)
        _columns = const.COLUMNS_REQUEST_SUBMITTED
    # print
    columns = ctx.columns or _columns
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        if instances > 1:
            ctx.wait_for_requests_to(obj)
        else:
            ctx.wait_for_request_to(obj)


@compute_vm_mk.command('from-clone', short_help='Create vm from clone')
@c_so.source_opt
@c_so.description_opt
@c_so.bill_dept_nr_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_nr_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.folder_nr_opt
@c_so.disks_nr_opt
@c_so.networks_nr_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.custom_spec_opt
@c_so.extra_config_opt
@c_so.vss_service_opt
@c_so.instances
@click.argument('name', type=click.STRING, required=False)
@pass_context
def compute_vm_mk_clone(
    ctx: Configuration,
    name,
    source,
    description,
    bill_dept,
    usage,
    memory,
    cpu,
    folder,
    disk,
    notes,
    admin,
    inform,
    net,
    domain,
    os,
    custom_spec,
    extra_config,
    vss_service,
    instances,
):
    """Clone virtual machine from running or powered off vm.
    If name argument is not specified, -clone suffix will be added to
    resulting virtual machine"""
    # get source from uuid or name
    _vm = ctx.get_vm_by_uuid_or_name(source)
    vm_uuid = _vm[0]['uuid']
    # payload
    payload = dict(
        description=description, name=name, usage=usage, source=vm_uuid
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = cpu
    if disk:
        payload['disks'] = list(disk)
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if bill_dept:
        payload['bill_dept'] = bill_dept
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if custom_spec:
        payload['custom_spec'] = custom_spec
    if instances > 1:
        payload['count'] = instances
        obj = ctx.create_vms_from_clone(**payload)
        _columns = const.COLUMNS_REQUEST_MULT_SUBMITTED
    else:
        # request
        obj = ctx.create_vm_from_clone(**payload)
        _columns = const.COLUMNS_REQUEST_SUBMITTED
    # print
    columns = ctx.columns or _columns
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        if instances > 1:
            ctx.wait_for_requests_to(obj)
        else:
            ctx.wait_for_request_to(obj)


@compute_vm_mk.command(
    'from-image', short_help='Create vm from OVA/OVF image.'
)
@click.argument('name', type=click.STRING, required=False)
@c_so.source_image_opt
@c_so.description_opt
@c_so.bill_dept_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.folder_opt
@c_so.disks_opt
@c_so.networks_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.custom_spec_opt
@c_so.extra_config_opt
@c_so.user_data_opt
@c_so.vss_service_opt
@pass_context
def compute_vm_mk_image(
    ctx: Configuration,
    name,
    source,
    description,
    bill_dept,
    usage,
    memory,
    cpu,
    folder,
    disk,
    notes,
    admin,
    inform,
    net,
    domain,
    os,
    custom_spec,
    extra_config,
    user_data,
    vss_service,
):
    """Deploy virtual machine from image"""
    # get reference to image by
    image_ref = ctx.get_vm_image_by_name_or_id_path(source)
    # payload
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        bill_dept=bill_dept,
        image=image_ref[0]['path'],
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = cpu
    if disk:
        payload['disks'] = list(disk)
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if custom_spec:
        payload['custom_spec'] = custom_spec
    if user_data:
        payload['user_data'] = user_data.read()
    # request
    obj = ctx.create_vm_from_image(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)
