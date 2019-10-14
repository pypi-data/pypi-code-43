# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
import click

__all__ = (
    'info',
    'error',
    'echo',
    'debug',
    'warn',
    'prompt',
    'succeed',
    'color_print'
)


def info(s, bold=False):
    click.secho(s, fg='cyan', bold=bold)

def error(s, bold=False):
    click.secho(s, fg='red', bold=bold)

def echo(s):
    click.secho(s)

def warn(s, bold=False):
    click.secho(s, fg='yellow', bold=bold)

def prompt(s, bold=False):
    click.secho(s, fg='blue', bold=bold)

def succeed(s, bold=False):
    click.secho(s, fg='green', bold=bold)

def color_print(s, fg='white', bold=False):
    click.secho(s, fg=fg, bold=bold)

DEBUG = bool(os.getenv('DEBUG', False))


def debug(s, bold=False):
    if DEBUG:
        click.secho('[DEBUG] {}'.format(s), fg='green', bold=False)