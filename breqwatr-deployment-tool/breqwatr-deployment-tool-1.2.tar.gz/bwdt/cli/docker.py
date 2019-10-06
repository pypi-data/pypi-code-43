""" Commands for operating Docker on the host """
# pylint disable=broad-except,W0703
import click

from bwdt.lib.container import Docker


@click.group(name='docker')
def docker_group():
    """ Command group for local docker commands """


@click.argument('repository')
@click.option('--tag', default=None,
              help='optional tag to pull, default=(current stable)')
@click.command(name='pull')
def pull_one(repository, tag):
    """ Pull an image from the upstream registry """
    Docker().pull(repository=repository, tag=tag)


@click.option('--tag', default=None, required=False,
              help='optional tag to pull. Default=(current stable)')
@click.command(name='pull-all')
def pull_all(tag):
    """ Pull all images """
    Docker().pull_all(tag=tag)


@click.argument('repository')
@click.option('--tag', required=False, help='Image tag', default=None)
@click.option('--pull/--no-pull', required=False, default=True,
              help='Use --no-pull to keep older image for this export')
@click.option('--force/--keep-old', required=False, default=False,
              help='--force will overwrite files found at the destination')
@click.command(name='export-image')
def export_image(repository, tag, pull, force):
    """ Export an image to directory """
    client = Docker()
    if pull:
        client.pull(repository=repository, tag=tag)
    client.export_image(repository, tag=tag, force=force)

@click.option('--pull/--no-pull', required=False, default=True,
              help='Use --no-pull to keep older image for this export')
@click.option('--tag', default=None, required=False,
              help='optional tag to pull. Default=(current stable)')
@click.option('--force/--keep-old', required=False, default=False,
              help='--force will overwrite files found at the destination')
@click.command(name='export-image-all')
def export_image_all(pull, tag, force):
    """ Export all images to directory  """
    client = Docker()
    if pull:
        client.pull_all(tag=tag)
    client.export_image_all(tag=tag, force=force)


docker_group.add_command(pull_one)
docker_group.add_command(pull_all)
docker_group.add_command(export_image)
docker_group.add_command(export_image_all)
