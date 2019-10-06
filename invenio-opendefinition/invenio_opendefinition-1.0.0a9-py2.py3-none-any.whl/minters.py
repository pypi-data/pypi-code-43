# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PID minters for Invenio-OpenDefinition."""

from __future__ import absolute_import, print_function

from invenio_pidstore.models import PersistentIdentifier, PIDStatus


def license_minter(record_uuid, data):
    """Mint a persistent identifier for a license."""
    return PersistentIdentifier.create(
        'od_lic',
        data['id'],
        object_type='rec',
        object_uuid=record_uuid,
        status=PIDStatus.REGISTERED
    )
