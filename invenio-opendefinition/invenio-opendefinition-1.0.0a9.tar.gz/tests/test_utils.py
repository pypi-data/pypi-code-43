# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test utilities."""

from __future__ import absolute_import, print_function

from invenio_opendefinition.loaders import harvest_spdx
from invenio_opendefinition.utils import obj_or_import_string


def test_obj_or_import_string():
    """Test object or string import utility function."""
    assert obj_or_import_string(harvest_spdx) == harvest_spdx
    assert obj_or_import_string(None, default=harvest_spdx) == harvest_spdx
    assert obj_or_import_string(
        'invenio_opendefinition.loaders.harvest_spdx') == harvest_spdx
