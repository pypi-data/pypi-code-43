# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test schema."""

from __future__ import absolute_import, print_function

from invenio_opendefinition.validators import license_validator


def test_licenses_schema(od_licenses_json):
    """Test that license schema validates the example file."""
    for key in od_licenses_json:
        license_validator.validate(od_licenses_json[key])
