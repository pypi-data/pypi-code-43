# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks."""

from __future__ import absolute_import, print_function

from celery import shared_task
from invenio_db import db

from .loaders import upsert_license_record
from .proxies import current_opendefinition


@shared_task(ignore_result=True)
def create_or_update_license_record(license):
    """Register a license."""
    upsert_license_record(license)
    db.session.commit()


@shared_task(ignore_result=True)
def harvest_licenses(source, path=None, eager=False):
    """Harvest licenses from a source."""
    licenses = current_opendefinition.loaders[source](filepath=path)
    for _, license in licenses.items():
        task = create_or_update_license_record.s(license)
        if eager:
            task.apply(throw=True)
        else:
            task.apply_async()
