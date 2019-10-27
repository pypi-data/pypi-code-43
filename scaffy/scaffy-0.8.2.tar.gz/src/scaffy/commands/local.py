# -*- coding: utf-8 -*-
""" Basic commands.
TODO:
    - Add optional fields.
        - On creating you specify pairs of name_in_src=field_name, The marker
          must include the field name somehow.
        - On applying during the read, once a marker is encountered the first
          time, the user us prompted for the value. Then that value is used
          for all subsequent occurrences.
"""
from __future__ import absolute_import, unicode_literals

import json

# 3rd party imports
import click

# local imports
from scaffy import remote
from scaffy import scaffold
from scaffy.core import log
from scaffy.core import shell
from . import cli


@cli.command('info')
@click.argument('name', type=str, required=True)
@click.option(
    '-f', '--files', 'show_files',
    is_flag=True,
    help='Show the list of files in the scaffold'
)
@click.option(
    '-c', '--config', 'show_config',
    is_flag=True,
    help='Show scaffold config'
)
def info(name, show_files, show_config):
    """ Show details about a given scaffold

    Example:

        \033[1mscaffy info -cf my-scaffold \033[0m

    This will show the full information about 'my-scaffold' scaffold. This
    includes the scaffold config as well as a list of scaffold files.
    """
    store = scaffold.LocalStore()
    item = store.load(name)

    log.info("Name:     ^33{}", item.name)
    log.info("Size:     ^33{} kb", round(item.size / 1024))
    log.info("Created:  ^33{}", item.pretty_created)

    if show_config:
        shell.cprint("Config: {")
        for key, value in item.json_config.items():
            shell.cprint('  "{name}": ^33{value}^0'.format(
                name=key, value=json.dumps(value, indent=2)
            ))

        shell.cprint("}")

    if show_files:
        log.info("Files:")
        for path in item.files:
            if path in item.marked_files:
                log.info('  ^0{}', path)
            else:
                log.info('  ^90{}', path)


@cli.command('delete')
@click.argument('names', nargs=-1, type=str, required=True)
@remote.print_api_errors
def delete(names):
    """ Delete selected scaffolds from the local store.

    Calling with multiple names will delete all of them with one command.
    """
    for name in names:
        log.info("Deleting ^35{}".format(name))
        store = scaffold.LocalStore()
        store.delete(name)


@cli.command('list')
def list_scaffolds():
    """ List scaffolds in local store. """
    local = scaffold.LocalStore()

    shell.cprint("^32Local:\n^0")
    for item in local.scaffolds:
        shell.cprint("  ^90{}  ^0{}", item.created, item.name)

    shell.cprint('')
