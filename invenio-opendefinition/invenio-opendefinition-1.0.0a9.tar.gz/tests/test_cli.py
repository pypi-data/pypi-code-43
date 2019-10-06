# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test CLI."""

from __future__ import absolute_import, print_function

from click.testing import CliRunner
from invenio_pidstore.models import PersistentIdentifier

from invenio_opendefinition.cli import opendefinition
from invenio_opendefinition.resolvers import license_resolver


def test_loadlicenses(script_info, license_server_mock,
                      od_licenses_path, od_licenses_json,
                      spdx_licenses_path, spdx_licenses_json):
    """Test load licenses."""
    assert PersistentIdentifier.query.count() == 0
    runner = CliRunner()
    license_pids = set()

    # Load opendefinition.org licenses twice (from URL and path)
    for cli_extra_args in ([], ['--path', od_licenses_path, '--eager']):
        result = runner.invoke(
            opendefinition,
            ['loadlicenses'] + cli_extra_args,
            obj=script_info
        )
        assert result.exit_code == 0
        for license_id, license in od_licenses_json.items():
            for license_id_variant in (license_id, license_id.lower()):
                pid, record = license_resolver.resolve(license_id_variant)
                assert record['title'] == license['title']
                assert record['url'] == license['url']
                assert record['id'] == license['id']
                license_pids.add(pid.pid_value)

    assert PersistentIdentifier.query.count() == len(license_pids)

    # Load spdx.org licenses twice (from URL and path)
    for cli_extra_args in ([], ['--path', spdx_licenses_path, '--eager']):
        result = runner.invoke(
            opendefinition,
            ['loadlicenses', '--source', 'spdx'] + cli_extra_args,
            obj=script_info
        )
        assert result.exit_code == 0
        for license in spdx_licenses_json['licenses']:
            license_id = license['licenseId']
            for license_id_variant in (license_id, license_id.lower()):
                pid, record = license_resolver.resolve(license_id_variant)
                assert record['title'] == license['name']
                assert record['url'] == license['seeAlso'][-1]
                assert record['id'] == license_id
                license_pids.add(license_id_variant)

    assert PersistentIdentifier.query.count() == len(license_pids)
