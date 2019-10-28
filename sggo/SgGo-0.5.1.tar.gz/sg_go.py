#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import click
from sggo import app

@click.group()
@click.pass_context
def cli(ctx):
    """ Plumber SG: a command-line tool for the View Plumber SG. """
    click.echo('Please report any bug or issue to <wei.zou@corerain.com>')

@cli.command()
@click.argument('sg_json', type=click.Path(exists=True))
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=5000)
def view(sg_json, host, port):
    app.run(sg_json, host, port)

if __name__ == '__main__':
    cli()
