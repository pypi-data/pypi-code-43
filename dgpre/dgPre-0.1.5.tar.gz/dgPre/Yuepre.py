#!/usr/bin/env python
import click

@click.command()
@click.option('--c', default=1, help='Number of print.')
@click.option('--n', prompt='Your entry',
              help='The help info to greet.')
def isCommand(c, n):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(c):
        click.echo('Your print n is %s!' % n)

if __name__ == '__main__':
    isCommand()