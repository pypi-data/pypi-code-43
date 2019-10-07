# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CIS UCT Prague.
#
# CIS theses repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""

from __future__ import absolute_import, print_function

import json
import uuid

from invenio_files_rest.models import ObjectVersion
from marshmallow import fields, missing, Schema, pre_load, post_dump


# noinspection PyUnusedLocal
def get_id(obj, context):
    """Get record id."""
    pid = context.get('pid')
    return pid.pid_value if pid else missing


class InvenioRecordSchemaV1Mixin(Schema):
    """Invenio record"""

    id = fields.String(required=True, validate=[lambda x: uuid.UUID(x)])
    _bucket = fields.String(required=False)
    _files = fields.Raw(dump_only=True)

    @pre_load
    def handle_load(self, instance):
        instance.pop('_files', None)

        #
        # modified handling id from default invenio way:
        #
        # we need to use the stored id in dump (in case the object
        # is referenced, the id should be the stored one, not the context one)
        #
        # for data loading, we need to overwrite the id by the context - to be sure no one
        # is trying to overwrite the id
        #
        id_ = get_id(instance, self.context)
        if id_ is not missing:
            instance['id'] = id_
        else:
            instance.pop('id', None)
        print(json.dumps(instance, indent=4))
        return instance
