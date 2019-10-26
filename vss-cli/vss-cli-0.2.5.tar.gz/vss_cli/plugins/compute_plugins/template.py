import logging

import click

from vss_cli import const, rel_opts as so
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.helper import format_output, process_filters
from vss_cli.plugins.compute import cli

_LOGGING = logging.getLogger(__name__)


@cli.group('template', short_help='List virtual machine templates')
@pass_context
def compute_template(ctx):
    """List virtual machine templates"""
    pass


@compute_template.command('ls', short_help='List virtual machine templates')
@so.filter_opt
@so.all_opt
@so.page_opt
@so.sort_opt
@so.count_opt
@pass_context
def compute_template_ls(
    ctx: Configuration, filter_by, show_all, sort, page, count
):
    """List virtual machine templates.

        Filter and sort list by any attribute. For example:

        vss-cli compute template ls -f name like,%vm-name% -f version like,%13

        Simple name filtering:

        vss-cli compute template ls -f name %vm-name% -s name desc

    """
    params = dict(expand=1, sort='name,asc')
    if all(filter_by):
        params['filter'] = ','.join(process_filters(filter_by))
    if all(sort):
        params['sort'] = f'{sort[0]},{sort[1]}'
    # get templates
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_templates(show_all=show_all, per_page=count, **params)
    # including additional attributes?
    columns = ctx.columns or const.COLUMNS_VM_TEMPLATE
    # format output
    output = format_output(ctx, obj, columns=columns)
    # page
    if page:
        click.echo_via_pager(output)
    else:
        click.echo(output)
