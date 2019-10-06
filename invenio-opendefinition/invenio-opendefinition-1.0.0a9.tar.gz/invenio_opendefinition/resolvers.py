# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resolvers for Invenio-OpenDefinition."""

from __future__ import absolute_import, print_function

import jsonresolver
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record
from werkzeug.routing import Rule

license_resolver = Resolver(
    pid_type='od_lic', object_type='rec', getter=Record.get_record
)


def resolve_license_jsonref(pid):
    """Resolve a license JSONref."""
    _, record = license_resolver.resolve(pid)
    return record


@jsonresolver.hookimpl
def jsonresolver_loader(url_map):
    """Resolve OpenDefinition licenses."""
    from flask import current_app
    url_map.add(Rule(
        '/licenses/<path:pid>',
        endpoint=resolve_license_jsonref,
        host=current_app.config['OPENDEFINITION_JSONRESOLVER_HOST']))
