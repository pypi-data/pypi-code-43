#
# Copyright (c) 2013-2019 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.

from marshmallow import fields, Schema


class ProbeResultSchema(Schema):
    id = fields.UUID(attribute="external_id")
    plateform = fields.String()
    version = fields.String()
    hostname = fields.String()

    status = fields.Integer()
    duration = fields.Float()

    error = fields.String(allow_none=True)
    results = fields.Field()

    artifacts = fields.Nested('ArtifactSchema', many=True)

    probe = fields.Nested('ProbeSchema')
