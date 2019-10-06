# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from __future__ import absolute_import, print_function

import json

from invenio_pidstore.models import PersistentIdentifier
from invenio_records_rest import InvenioRecordsREST
from invenio_records_rest.views import create_blueprint

from invenio_opendefinition.config import OPENDEFINITION_REST_ENDPOINTS


def test_records_rest(app, es, loaded_example_licenses):
    """Test Records REST."""
    app.config['RECORDS_REST_ENDPOINTS'] = OPENDEFINITION_REST_ENDPOINTS
    InvenioRecordsREST(app)
    # invenio-records-rest >= 1.1.0 doesn't automatically register endpoints
    app_endpoints = app.url_map._rules_by_endpoint
    if 'invenio_records_rest.od_lic_item' not in app_endpoints:
        app.register_blueprint(create_blueprint(OPENDEFINITION_REST_ENDPOINTS))

    assert PersistentIdentifier.query.count() == 202

    with app.test_client() as client:
        for license_id in ('MIT', 'mit'):
            resp = client.get('/licenses/{}'.format(license_id))
            assert resp.status_code == 200
            resp_json = json.loads(resp.get_data(as_text=True))
            assert resp_json['metadata'] == loaded_example_licenses['MIT']

            resp = client.get('/licenses/')
            resp_json = json.loads(resp.get_data(as_text=True))
            assert resp.status_code == 200
            assert resp_json['hits']['total'] == 109

            resp = client.get('/licenses/_suggest?text=mit')
            resp_json = json.loads(resp.get_data(as_text=True))
            assert resp.status_code == 200
            options = resp_json['text'][0]['options']
            assert len(options) == 2
            assert {
                (o['_source']['id'], o['_source']['title']) for o in options
            } == {
                ('MIT', 'MIT License'),
                ('mitre',
                 'MITRE Collaborative Virtual Workspace License (CVW License)')
            }

            resp = client.get('/licenses/_suggest?text=cc0')
            resp_json = json.loads(resp.get_data(as_text=True))
            assert resp.status_code == 200
            options = resp_json['text'][0]['options']
            assert len(options) == 1
            assert {
                (o['_source']['id'], o['_source']['title'])
                for o in options} == {('CC0-1.0', 'CC0 1.0'), }
