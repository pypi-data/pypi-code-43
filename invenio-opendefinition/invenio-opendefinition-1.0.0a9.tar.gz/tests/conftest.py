# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import json
import os
import shutil
import tempfile
from os.path import dirname, join

import httpretty
import pytest
from elasticsearch.exceptions import RequestError
from flask import Flask
from flask.cli import ScriptInfo
from flask_celeryext import FlaskCeleryExt
from invenio_db import InvenioDB, db
from invenio_indexer import InvenioIndexer
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_pidstore import InvenioPIDStore
from invenio_records import InvenioRecords
from invenio_records_rest.utils import PIDConverter
from invenio_search import InvenioSearch, current_search
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from invenio_opendefinition import InvenioOpenDefinition
from invenio_opendefinition.loaders import upsert_license_record


@pytest.yield_fixture
def app(od_licenses_json):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    app = Flask('testapp', instance_path=instance_path)
    app.config.update(
        JSONSCHEMAS_HOST='localhost',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite://'),
        TESTING=True,
        RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY=None,
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND="cache",
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    )

    app.url_map.converters['pid'] = PIDConverter

    FlaskCeleryExt(app)
    InvenioDB(app)
    InvenioJSONSchemas(app)
    InvenioRecords(app)
    InvenioIndexer(app)
    InvenioPIDStore(app)
    InvenioOpenDefinition(app)

    with app.app_context():
        if str(db.engine.url) != "sqlite://" and \
           not database_exists(str(db.engine.url)):
            create_database(str(db.engine.url))

        # MySQL has case-sensitivity issues with its default collation. To fix
        # this, we alter the created database's charset and collation.
        if str(db.engine.url).startswith('mysql'):
            conn = db.engine.connect()
            conn.execute('COMMIT')  # close the current transaction
            conn.execute('ALTER DATABASE invenio '
                         'CHARACTER SET utf8 COLLATE utf8_bin')
            conn.close()
        db.drop_all()
        db.create_all()

    def teardown():
        drop_database(str(db.engine.url))

    yield app

    shutil.rmtree(instance_path)


@pytest.yield_fixture
def script_info(app):
    """CLI object."""
    with app.app_context():
        yield ScriptInfo(create_app=lambda info: app)


@pytest.fixture
def loaded_example_licenses(app, es, od_licenses_json):
    license_records = {}
    with app.app_context():
        for key, license in od_licenses_json.items():
            license_records[key] = upsert_license_record(license)
            db.session.commit()
            RecordIndexer().index_by_id(license_records[key].id)
    es.flush_and_refresh('licenses')
    return license_records


@pytest.yield_fixture
def license_server_mock(app, od_licenses_json, spdx_licenses_json):
    httpretty.register_uri(
        httpretty.GET,
        app.config['OPENDEFINITION_LICENSES_URL'],
        body=json.dumps(od_licenses_json),
        content_type='application/json'
    )
    httpretty.register_uri(
        httpretty.GET,
        app.config['OPENDEFINITION_SPDX_LICENSES_URL'],
        body=json.dumps(spdx_licenses_json),
        content_type='application/json'
    )
    httpretty.enable()
    yield
    httpretty.disable()


@pytest.fixture(scope="session")
def od_licenses_path():
    return join(dirname(__file__), 'data', 'opendefinition.json')


@pytest.fixture(scope="session")
def od_licenses_json(od_licenses_path):
    with open(od_licenses_path) as file:
        return json.load(file)


@pytest.fixture(scope="session")
def spdx_licenses_path():
    return join(dirname(__file__), 'data', 'spdx.json')


@pytest.fixture(scope="session")
def spdx_licenses_json(spdx_licenses_path):
    with open(spdx_licenses_path) as file:
        return json.load(file)


@pytest.yield_fixture
def es(app):
    """Provide elasticsearch access."""
    app.config.update(dict(
        SEARCH_AUTOINDEX=[],
    ))
    InvenioSearch(app)
    with app.app_context():
        try:
            list(current_search.create())
        except RequestError:
            list(current_search.delete(ignore=[404]))
            list(current_search.create())
        yield current_search
        list(current_search.delete(ignore=[404]))
