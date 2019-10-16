"""
Cli module
"""

from __future__ import absolute_import, division, print_function

import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-b", "--bold", is_flag=True, help="Print text in bold?")
@click.option("-c", "--color", required=True, type=click.Choice(["green", "yellow", "red"]), help="Text color.")
@click.option("-t", "--text", required=True, help="Text to print.")
@click.version_option()
def main(bold, color, text):
    """ print text in color and optionally in bold """

    click.secho(text, fg=color, bold=bold)
