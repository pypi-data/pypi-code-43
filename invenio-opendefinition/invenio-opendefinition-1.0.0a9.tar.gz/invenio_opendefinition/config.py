# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module integrating Invenio repositories and OpenDefinition."""

from __future__ import absolute_import, print_function

OPENDEFINITION_LICENSES_URL = \
    'http://licenses.opendefinition.org/licenses/groups/all.json'

OPENDEFINITION_SPDX_LICENSES_URL = 'https://spdx.org/licenses/licenses.json'

OPENDEFINITION_LOADERS = {
    'opendefinition': 'invenio_opendefinition.loaders.harvest_opendefinition',
    'spdx': 'invenio_opendefinition.loaders.harvest_spdx',
}

OPENDEFINITION_SCHEMAS_DEFAULT_LICENSE = 'licenses/license-v1.0.0.json'

OPENDEFINITION_JSONRESOLVER_HOST = 'inveniosoftware.org'

OPENDEFINITION_REST_ENDPOINTS = dict(
    od_lic=dict(
        pid_type='od_lic',
        pid_minter='opendefinition_license_minter',
        pid_fetcher='opendefinition_license_fetcher',
        list_route='/licenses/',
        item_route='/licenses/<pid(od_lic):pid_value>',
        search_index='licenses',
        search_type=None,
        record_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_response'),
        },
        search_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_search'),
        },
        default_media_type='application/json',
        suggesters={
            'text': {
                'completion': {
                    'field': 'suggest',
                }
            }
        },
    ),
)
