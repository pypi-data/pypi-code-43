"""
Entrypoint for the bbcli tool
"""

import click

from brewblox_deploy import cli_docker, cli_git

cli = click.CommandCollection(
    sources=[
        cli_git.cli,
        cli_docker.cli,
    ])


if __name__ == '__main__':
    cli()
