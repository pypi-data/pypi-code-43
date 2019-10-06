"""Commands for operating the local registry"""
import requests

import click

import bwdt.services.registry as registry


@click.group(name='registry')
def registry_group():
    """Command group for bwdt registry"""


@click.option('--ip', default='0.0.0.0', help='optional bind IP address')
@click.option('--port', default='5000', help='optional bind port')
@click.command()
def start(ip, port):
    """Launch the local registry"""
    click.echo("Launching container: registry")
    success = registry.start(ip, port)
    if success:
        click.echo('Done')
    else:
        click.echo('Failed to launch - Maybe its already running?')


@click.argument('image_name')
@click.argument('registry_url')
@click.option('--tag', default=None, help='optional image tag')
@click.command(name='sync-openstack-image')
def sync_image(image_name, registry_url, tag):
    """ Load image_name and push it to the local registry """
    click.echo('Sync {} to {}...'.format(image_name, registry_url))
    registry.sync_image(image=image_name, registry_url=registry_url, tag=tag)


@click.argument('registry_url')
@click.option('--tag', default=None, help='optional image tag')
@click.command(name='sync-all-openstack-images')
def sync_all_images(registry_url, tag):
    """ Load all images and push them to the local registry """
    click.echo('Pushing all images to {}'.format(registry_url))
    registry.sync_all_images(registry_url=registry_url, tag=tag)


@click.argument('registry_url')
@click.command(name='list-images')
def list_images(registry_url):
    """ List the images in a registry """
    if 'http' not in registry_url:
        registry_url = 'http://{}'.format(registry_url)
    catalog_url = '{}/v2/_catalog'.format(registry_url)
    response = requests.get(url=catalog_url)
    repositories = response.json()['repositories']
    for repo in repositories:
        click.echo('{}'.format(repo))
        tags_url = '{}/v2/{}/tags/list'.format(registry_url, repo)
        tag_resp = requests.get(url=tags_url)
        tags = tag_resp.json()['tags']
        for tag in tags:
            click.echo('  - {}'.format(tag))


registry_group.add_command(start)
registry_group.add_command(sync_image)
registry_group.add_command(sync_all_images)
registry_group.add_command(list_images)
