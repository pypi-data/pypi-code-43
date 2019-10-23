#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from marshmallow import fields, Schema


class UserSchema(Schema):
    username = fields.String()
    password = fields.String()
    email = fields.Email()
    full_name = fields.String()
    permissions = fields.List(fields.String)
    timezone = fields.String()
    session_timeout_ms = fields.Integer()
    startpage = fields.Raw()
    roles = fields.List(fields.String)


class RoleSchema(Schema):
    name = fields.String()
    description = fields.String()
    permissions = fields.List(fields.String)
    read_only = fields.Boolean(default=True)


class DashboardSchema(Schema):
    title = fields.String()
    description = fields.String()


class DashboardWidgetSchema(Schema):
    description = fields.String()
    type = fields.String()
    cache_time = fields.Integer()
    config = fields.Raw()


class DashboardPositionSchema(Schema):
    positions = fields.List(fields.Raw)


class StreamRuleSchema(Schema):
    type = fields.Integer()
    value = fields.String()
    field = fields.String()
    inverted = fields.Boolean(default=False)


class StreamSchema(Schema):
    title = fields.String()
    description = fields.String()
    rules = fields.List(fields.Nested(StreamRuleSchema))
    content_pack = fields.String()
    index_set_id = fields.String()
    remove_matches_from_default_stream = fields.Boolean(default=False)
    matching_type = fields.String(validate=lambda x: x in ['AND', 'OR'])


class AlertConditionSchema(Schema):
    type = fields.String()
    title = fields.String()
    parameters = fields.Raw()


class AlertReceiverSchema(Schema):
    entity = fields.String(required=True)
    type = fields.String(validate=lambda x: x in ('users', 'emails'))
