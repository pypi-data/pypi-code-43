""" Commands to configure BWDT """
import click

import bwdt.lib.configure


@click.option('--key-id', help='Auth Key ID', default=None)
@click.option('--key', help='Auth Key', default=None)
@click.option('--online/--offline', help='Online/Offline mode', default=True)
@click.option('--offline-path', default=None,
              help='Path to offline installer files')
@click.command()
def configure(key_id, key, online, offline_path):
    """ Launch the configuration setup """
    bwdt.lib.configure.configure(key_id, key, online, offline_path)
