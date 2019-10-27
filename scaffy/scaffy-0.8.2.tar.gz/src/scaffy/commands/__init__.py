# -*- coding: utf-8 -*-
""" Commands package.

All commands (and only commands) should be defined inside this package. This
should be as thin layer as possible. Ideally just processing CLI params and
displaying results.
"""
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import click

# local imports
import scaffy
from scaffy.config import settings


@click.group()
@click.version_option(version=scaffy.__version__, message='%(version)s')
def cli():
    """

    To get help for a specific command:

        \033[1mscaffy <command> --help\033[0m

    Examples:

        \033[1mscaffy create --help . --help\033[0m

        \033[1mscaffy push --help\033[0m

    """
    settings.load()
    pass
