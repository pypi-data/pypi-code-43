# -*- coding: utf-8 -*-
""" Commands for interacting with the remote service. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
import os
import sys

# 3rd party imports
import click

# local imports
from scaffy import remote
from scaffy import scaffold
from scaffy.core import log
from scaffy.core import shell
from scaffy.scaffold import Scaffold
from . import cli


@cli.group('hub')
def hub_cli():
    """ ScaffyHub commands. """
    pass


@hub_cli.command()
@click.option(
    '-u', '--username',
    type=str,
    prompt='Username',
    help='scaffyhub username'
)
@click.option(
    '-p', '--password',
    type=str,
    prompt='Password',
    hide_input=True,
    help='scaffyhub password'
)
@remote.print_api_errors
def login(username, password):
    """ Login to scaffyhub.

    After login the authorization token will be stored in scaffy ~/.config
    directory for future use. The username/password is not stored anywhere and
    once the token expires the user will log again. The app supports rolling
    session so every time you interact with scaffyhub you will get the new token
    and your session time will be extended.
    """
    api = remote.Client()

    log.info("Authenticating with {}".format(api.backend_url))
    api.login(username, password)
    log.info("Logged in")


@hub_cli.command()
@click.argument('name', type=str)
@remote.print_api_errors
def push(name):
    """ Push scaffold to scaffyhub.

    The scaffold file will be uploaded to scaffyhub. You can then pull that
    scaffold from any machine using `scaffy pull`.
    """
    local_store = scaffold.LocalStore()
    api = remote.Client()

    item = local_store.load(name)

    # Upload the scaffold
    log.info("Uploading ^35{} ^32to ^34{}".format(item.name, api.backend_url))
    try:
        api.scaffold.upload(item)
        log.info("Done")
        # shell.cprint('^33[{}]: ^90{}', 200, json.dumps(
        #     remote_item.serialize(), indent=2
        # ))
    except remote.ApiError as ex:
        log.err("[{status}] {detail}:\n{body}".format(
            status=ex.response.status_code,
            detail=str(ex),
            body=json.dumps(ex.response.json(), indent=2)
        ))


@hub_cli.command()
@click.argument('name', type=str)
@remote.print_api_errors
def pull(name):
    """ Pull a scaffold with the given name from scaffyhub. """
    local_store = scaffold.LocalStore()
    api = remote.Client()

    remote_item = api.scaffold.get_by_name(name)

    if remote_item is None:
        log.err("'{}' does not exist".format(name))
        sys.exit(-1)

    temp_path = remote_item.download()
    item = Scaffold.load_from_file(temp_path)

    # This will physically write the scaffold file to a local store, thus
    # making a copy so the original can be deleted.
    local_store.add(item)
    os.remove(temp_path)


@hub_cli.command('list')
@remote.print_api_errors
def hub_list():
    """ List scaffolds locally on the hub. """
    api = remote.Client()

    shell.cprint("^32Remote:\n^0")
    for item in api.scaffold.list():
        shell.cprint("  ^90{}  ^0{}", item.created, item.name)

    shell.cprint('')


@hub_cli.command('delete')
@click.argument('names', nargs=-1, type=str, required=True)
def hub_delete(names):
    """ Delete selected scaffolds from the hub.

    Calling with multiple names will delete all of them with one command.
    """
    api = remote.Client()

    for remote_item in api.scaffold.list():
        if remote_item.name in names:
            try:
                remote_item.delete()
            except remote.ApiError as ex:
                log.err("[{status}] {detail}:\n{body}".format(
                    status=ex.response.status_code,
                    detail=str(ex),
                    body=ex.response.text
                ))
