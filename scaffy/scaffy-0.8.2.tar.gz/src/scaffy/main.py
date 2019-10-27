# -*- coding: utf-8 -*-
# pylint: disable=unused-import
""" The application entry point.

Setup completion and import all commands.
"""
from __future__ import absolute_import, unicode_literals

# local imports
from scaffy.commands import cli
__all__ = [
    'cli'
]


from scaffy.commands import scaffold    # noqa
from scaffy.commands import local       # noqa
from scaffy.commands import remote      # noqa
