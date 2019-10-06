# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module integrating Invenio repositories and OpenDefinition."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_indexer.signals import before_record_index
from werkzeug.utils import cached_property

from . import config
from .cli import opendefinition
from .indexer import indexer_receiver
from .utils import obj_or_import_string


class InvenioOpenDefinition(object):
    """Invenio-OpenDefinition extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    @cached_property
    def loaders(self):
        """License loaders dictionary."""
        loaders = current_app.config['OPENDEFINITION_LOADERS']
        return {k: obj_or_import_string(v) for k, v in loaders.items()}

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.cli.add_command(opendefinition)
        before_record_index.connect(indexer_receiver, sender=app)
        app.extensions['invenio-opendefinition'] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('OPENDEFINITION_'):
                app.config.setdefault(k, getattr(config, k))
