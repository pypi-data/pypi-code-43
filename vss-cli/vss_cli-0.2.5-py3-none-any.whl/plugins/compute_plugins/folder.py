import logging

import click

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.exceptions import VssCliError
from vss_cli.helper import format_output, process_filters
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('folder', short_help='Manage logical folders')
@pass_context
def compute_folder(ctx):
    """Logical Folders are containers for storing and organizing
    inventory objects, in this case virtual machines."""


@compute_folder.command('ls', short_help='list folders')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.page_opt
@pass_context
def compute_folder_ls(ctx: Configuration, filter_by, show_all, sort, page):
    """ List logical folders based on:

        Filter list in the following format <field_name> <operator>,<value>
        where operator is eq, ne, lt, le, gt, ge, like, in.

        For example: name like,%Project%

            vss-cli compute folder ls -f name like,%Project%

        Sort list in the following format <field_name> <asc|desc>. For example:

            vss-cli compute folder ls -s path desc
    """
    params = dict(expand=1, sort='path,asc')
    if all(filter_by):
        params['filter'] = ','.join(process_filters(filter_by))
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # get objects
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_folders(show_all=show_all, **params)
    # set columns
    columns = ctx.columns or const.COLUMNS_FOLDER_MIN
    # format
    output = format_output(ctx, obj, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@compute_folder.group('set', short_help='update folder')
@click.argument(
    'moref_or_name', type=click.STRING, autocompletion=autocompletion.domains
)
@so.wait_opt
@pass_context
def compute_folder_set(ctx, moref_or_name: str, wait: bool):
    """Update given folder attribute."""
    _folder = ctx.get_folder_by_name_or_moref_path(moref_or_name)
    ctx.moref = _folder[0]['moref']
    ctx.wait = wait


@compute_folder_set.command('parent', short_help='move folder')
@click.argument('parent-name-or-moref', type=click.STRING, required=True)
@pass_context
def compute_folder_set_parent(ctx: Configuration, parent_name_or_moref):
    """Move folder to given moref.
     Use to obtain parent folder:

       vss-cli compute folder ls

    """
    _LOGGING.debug(f'Attempting to move {ctx.moref} to {parent_name_or_moref}')
    # exist parent
    _folder = ctx.get_folder_by_name_or_moref_path(parent_name_or_moref)
    parent_moref = _folder[0]['moref']
    # create payload
    payload = dict(moref=ctx.moref, new_moref=parent_moref)
    obj = ctx.move_folder(**payload)
    # format output
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_folder_set.command('name', short_help='rename folder')
@click.argument('name', type=click.STRING, required=True)
@pass_context
def compute_folder_set_name(ctx: Configuration, name):
    """Rename folder to given name.
     Use to obtain parent folder:

       vss-cli compute folder ls

    """
    _LOGGING.debug(f'Attempting to rename {ctx.moref} to {name}')
    # exist folder
    payload = dict(moref=ctx.moref, name=name)
    obj = ctx.rename_folder(**payload)
    # format output
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_folder.command('rm', short_help='remove folder')
@click.argument(
    'moref',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.folders,
)
@pass_context
def compute_folder_rm(ctx, moref):
    """Delete a logical folder. Folder must be empty.
    Use to obtain folder moref:

       vss-cli compute folder ls

    """
    _LOGGING.debug(f'Attempting to remove {moref}')
    # exist folder
    payload = dict(moref=ctx.moref)
    obj = ctx.delete_folder(**payload)
    # format output
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait:
        ctx.wait_for_request_to(obj)


@compute_folder.command('mk', short_help='create folder')
@click.argument('name', type=click.STRING, required=True)
@click.option(
    '-p', '--parent', type=click.STRING, required=True, help='Parent folder'
)
@pass_context
def compute_folder_mk(ctx: Configuration, parent, name):
    """Create a logical folder under a given moref parent.
    Use to obtain parent folder:

       vss-cli compute folder ls

    """
    _LOGGING.debug(f'Attempting to create {name} under {parent}')
    # exist folder
    _folder = ctx.get_folder_by_name_or_moref_path(parent)
    obj = ctx.create_folder(moref=_folder[0]['moref'], name=name)
    # format output
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_folder.group(
    'get', help='Given folder info.', invoke_without_command=True
)
@click.argument(
    'moref_or_name',
    type=click.STRING,
    required=True,
    autocompletion=autocompletion.folders,
)
@pass_context
def compute_folder_get(ctx: Configuration, moref_or_name):
    _folder = ctx.get_folder_by_name_or_moref_path(moref_or_name)
    ctx.moref = _folder[0]['moref']
    if click.get_current_context().invoked_subcommand is None:
        obj = ctx.get_folder(ctx.moref)
        obj['moref'] = ctx.moref
        # set columns
        columns = ctx.columns or const.COLUMNS_FOLDER
        # format
        click.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_folder_get.command('vms', short_help='list virtual machines.')
@click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
@pass_context
def compute_folder_get_vms(ctx: Configuration, page):
    """List logical folder children virtual machines."""
    obj = ctx.get_vms_by_folder(ctx.moref)
    # format output
    columns = ctx.columns or const.COLUMNS_VM_MIN
    output = format_output(ctx, obj, columns=columns)
    # page
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@compute_folder_get.command('children', short_help='list children folders.')
@click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
@pass_context
def compute_folder_get_children(ctx: Configuration, page):
    """List logical folder immediate children folders."""
    obj = ctx.get_folder_children(ctx.moref)
    # format output
    columns = ctx.columns or const.COLUMNS_FOLDER_MIN
    output = format_output(ctx, obj, columns=columns)
    # page
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)


@compute_folder_get.command('perm', short_help='list permissions.')
@click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
@pass_context
def compute_folder_get_perms(ctx: Configuration, page):
    """Obtain logical folder group or user permissions."""
    obj = ctx.get_folder_permission(ctx.moref)
    if not obj:
        raise VssCliError(
            f'Either folder {ctx.moref} does not exist, '
            f'or you do not have permission to access.'
        )
    columns = ctx.columns or const.COLUMNS_PERMISSION
    output = format_output(ctx, obj, columns=columns)
    # page
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)
