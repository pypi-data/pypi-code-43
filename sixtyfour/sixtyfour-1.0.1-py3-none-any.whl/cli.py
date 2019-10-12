import click
import sys
from .sixtyfour import bytes_to_b64, b64_to_bytes


@click.command()
@click.option('--file', '-f', type=click.File('rb'))
@click.option('--decode', '-d', '-D', is_flag=True)
def main(file, decode):
    isatty = sys.stdin.isatty()

    if not isatty and file:
        raise click.ClickException('Can not feed from stdin and file at the same time')

    if not isatty:
        stdin = click.get_binary_stream('stdin').read().strip()
        click.echo(
            message=bytes_to_b64(stdin),
            nl=False
        )

    if file:
        if decode:
            click.echo(
                message=b64_to_bytes(file.read()),
                nl=False
            )
        else:
            click.echo(
                message=bytes_to_b64(file.read()),
                nl=False
            )
