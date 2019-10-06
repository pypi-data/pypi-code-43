""" Commands for downloading from s3 """
import click
import bwdt.lib.download


@click.group(name='download')
def download_group():
    """ Download files for offline install """


@click.argument('path')
@click.option('--force/--no-force', default=False,
              help='Use --force to overwrite file if it already exists')
@click.command(name='offline-apt')
def offline_apt(path, force):
    """ Download a subset of breqwatr/apt for offline installs """
    bwdt.lib.download.offline_apt(path, force)


@click.argument('path')
@click.option('--force/--no-force', default=False,
              help='Use --force to overwrite file if it already exists')
@click.command(name='offline-bwdt')
def offline_bwdt(path, force):
    """ Download an offline export of this bwdt tool """
    bwdt.lib.download.offline_bwdt(path, force)


@click.argument('path')
@click.option('--force/--no-force', default=False,
              help='Use --force to overwrite file if it already exists')
@click.command(name='cloud-yml')
def cloud_yml(path, force):
    """ Download a commented cloud.yml template """
    bwdt.lib.download.cloud_yml(path, force)


download_group.add_command(offline_apt)
download_group.add_command(offline_bwdt)
download_group.add_command(cloud_yml)
