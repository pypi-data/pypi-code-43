""" Commands for operating the Pip service """
import click

import bwdt.services.pip as pip


@click.group(name='pip')
def pip_group():
    """ Command group for bwdt Pip service """


@click.option('--tag', required=False, default=None, help='optional tag')
@click.command()
def start(tag):
    """Launch the Pip service"""
    click.echo("Launching container: pip")
    success = pip.start(tag)
    if success:
        click.echo('Done')
    else:
        click.echo('Failed to launch - Maybe its already running?')


pip_group.add_command(start)
