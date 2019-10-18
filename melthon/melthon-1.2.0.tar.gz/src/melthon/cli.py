"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mmelthon` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``melthon.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``melthon.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import logging
from pathlib import Path

import click

from melthon import core


@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Shows debug messages')
def main(verbose):
    """Minimalistic static site generator."""

    # Setup logger
    if verbose:
        logging.basicConfig(format='%(filename)s:%(lineno)d ▶ %(levelname)s: %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


@main.command()
@click.option('-o', '--output-dir', default='output', help='Directory to which rendered templates will be saved')
def clean(output_dir):
    core.clean(Path(output_dir))


@main.command()
@click.option('-t', '--templates-dir', default='templates', help='Directory which contains your Mako templates')
@click.option('-s', '--static-dir', default='static', help='Directory which contains your static assets')
@click.option('-d', '--data-dir', default='data', help='Directory which contains your YAML data files')
@click.option('-m', '--middleware-dir', default='middleware', help='Directory which contains your custom middlewares')
@click.option('-o', '--output-dir', default='output', help='Directory to which rendered templates will be saved')
@click.option('--pretty-urls/--no-pretty-urls', default=True,
              help='Pretty url will generate folders with index files. E.g. python/index.html instead of python.html')
def build(templates_dir, static_dir, data_dir, middleware_dir, output_dir, pretty_urls):
    core.build(Path(templates_dir), Path(static_dir), Path(data_dir), Path(middleware_dir), Path(output_dir), pretty_urls)
