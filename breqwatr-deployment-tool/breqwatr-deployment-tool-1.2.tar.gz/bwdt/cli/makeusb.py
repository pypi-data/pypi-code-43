""" Commands to configure BWDT """
import click

import bwdt.lib.download as download
from bwdt.lib.container import Docker


@click.argument('path')
@click.option('--force/--no-force', default=False,
              help='Use --force to overwrite files if they already exists')
@click.option('--tag', required=False, default=None,
              help='Optional tag override to build media for older versions')
@click.command(name='export-offline-media')
def makeusb(path, force, tag):
    """ Create an offline installer USB/Disk at specified path """
    click.echo('Exporting offline install files to {}'.format(path))
    download.cloud_yml(path, force)
    download.offline_bwdt(path, force)
    download.offline_apt(path, force)
    client = Docker()
    client.pull_all(tag=tag)
    client.export_image_all(tag=tag, force=force)
