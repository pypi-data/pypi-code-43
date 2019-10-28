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

from marshmallow import fields, Schema, post_load
from ..csts import ProbeCategory


class Probe:

    def __init__(self, *, external_id, name, display_name, category,
                 platform, version, timestamp_creation):
        self.external_id = str(external_id)
        self.name = name
        self.display_name = display_name
        self.category = ProbeCategory(category)
        self.platform = platform
        self.version = version
        self.timestamp_creation = timestamp_creation

    @property
    def id(self):
        return self.external_id

    def __repr__(self):
        return self.__class__.__name__ + "." + self.id

    def __str__(self):
        ret = "Probe{"
        ret += "id: {}; ".format(self.id)
        ret += "name: {}; ".format(self.name)
        ret += "display_name: {}; ".format(self.display_name)
        ret += "category: {}; ".format(self.category.value)
        ret += "platform: {}; ".format(self.platform)
        ret += "version: {}; ".format(self.version)
        ret += "timestamp_creation: {}; ".format(self.timestamp_creation)
        ret += "}"
        return ret

    def __eq__(self, other):
        return isinstance(other, Probe) and \
               self.name == other.name and \
               self.version == other.version

    def __ne__(self, other):
        return not (self == other)


class ProbeAntivirus(Probe):

    def __init__(self, *args, av_version=None, db_version=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.av_version = av_version
        self.db_version = db_version


class ProbeSchema(Schema):
    _obj = Probe

    @classmethod
    def dynschema(cls, data, **kwargs):
        """ Dynamically retrieve required schema
        :param data: data to unmarshall
        :returns: the required schema class
        """
        try:
            category = data["category"]
            if category == ProbeCategory.antivirus:
                return ProbeAntivirusSchema
            return cls
        except KeyError:
            return cls

    id = fields.UUID(attribute="external_id")
    name = fields.String()
    display_name = fields.String()
    category = fields.Function(
        serialize=lambda obj: (
            obj.category.value if isinstance(obj.category, ProbeCategory)
            else obj.category
        ),
        deserialize=lambda obj: obj
    )
    platform = fields.String()
    version = fields.String()
    timestamp_creation = fields.Number()

    @post_load
    def make_object(self, data, **kwargs):
        return self._obj(**data)


class ProbeAntivirusSchema(ProbeSchema):
    _obj = ProbeAntivirus
    av_version = fields.String()
    db_version = fields.String()
