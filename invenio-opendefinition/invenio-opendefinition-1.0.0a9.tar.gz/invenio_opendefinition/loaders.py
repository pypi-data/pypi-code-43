# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""License loaders."""

from __future__ import absolute_import, print_function

import json
from copy import deepcopy

import requests
from flask import current_app
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records.api import Record

from .minters import license_minter
from .resolvers import license_resolver
from .validators import license_validator


def upsert_license_record(license):
    """Insert or update a license record.

    For each license record, two Persistent Identifiers are minted: one for the
    original ``id`` field, and one for the lower-case version of the field.
    """
    license_validator.validate(license)
    license['$schema'] = 'http://{0}{1}/{2}'.format(
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config['JSONSCHEMAS_ENDPOINT'],
        current_app.config['OPENDEFINITION_SCHEMAS_DEFAULT_LICENSE']
    )

    # Check if a record already exists under one of the available license IDs
    license_ids_to_mint = set()
    license_ids = (license['id'], license['id'].lower())
    record = None
    for license_id in license_ids:
        try:
            _, record = license_resolver.resolve(license_id)
        except PIDDoesNotExistError:
            license_ids_to_mint.add(license_id)

    # If no license record was found under the existing aliases, create one
    if not record:
        record = Record.create(license)
    else:
        record.update(license)
        record.commit()

    for license_id in license_ids_to_mint:
        license_copy = deepcopy(record)
        license_copy['id'] = license_id
        license_minter(record.id, license_copy)
    return record


def harvest_opendefinition(filepath=None):
    """Harvest licenses from https://opendefinition.org."""
    if filepath:
        with open(filepath) as fp:
            od_licenses = json.load(fp)
    else:
        response = requests.get(
            current_app.config['OPENDEFINITION_LICENSES_URL'])
        od_licenses = response.json()
    return od_licenses


def harvest_spdx(filepath=None):
    """Harvest licenses from https://spdx.org."""
    if filepath:
        with open(filepath) as fp:
            spdx_payload = json.load(fp)
    else:
        response = requests.get(
            current_app.config['OPENDEFINITION_SPDX_LICENSES_URL'])
        spdx_payload = response.json()

    # Preprocess the SPDX licenses to conform to the OpenDefinition schema
    licenses = {}
    for l in spdx_payload['licenses']:
        licenses[l['licenseId']] = {
            'id': l['licenseId'],
            'url': l['seeAlso'][-1],  # Last link is the most recent/valid
            'title': l['name'],
            'family': '',
            'maintainer': '',
            'status': 'retired' if l['isDeprecatedLicenseId'] else 'active',
            'osd_conformance': ('approved' if l['isOsiApproved']
                                else 'not reviewed'),
            'od_conformance': 'not reviewed',
            'domain_content': False,
            'domain_data': False,
            'domain_software': False,
        }
    return licenses
