# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PID Fetchers tests."""

from __future__ import absolute_import, print_function

import uuid

from invenio_opendefinition.fetchers import license_fetcher


def test_license_fetcher():
    """Test license fetcher."""
    val = 'MIT'
    pid = license_fetcher(uuid.uuid4(), {'id': val})
    assert pid.provider is None
    assert pid.pid_type is 'od_lic'
    assert pid.pid_value is val
