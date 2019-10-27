# -*- coding: utf-8 -*-
"""
This is just so that all the configuration is in one place.

Changing the configuration will still require releasing new version.
"""

from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import expanduser

# local imports
from scaffy.core.config import Config


class ScaffyConfig(Config):
    """ Configuration for scaffy app. """

    resolution = [
        expanduser('~/.config/scaffy/config.yml'),
        '/etc/scaffy/config.yml',
    ]

    defaults = {
        'CREDENTIALS_PATH': expanduser('~/.config/scaffy/credentials'),
        'BACKENDS': [
            'http://localhost:12001',
            'https://scaffyhub.novocode.net',
        ]
    }


settings = ScaffyConfig()
