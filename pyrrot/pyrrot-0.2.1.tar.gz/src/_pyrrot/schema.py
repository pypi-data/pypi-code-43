from http import HTTPStatus

from marshmallow import Schema, fields
from marshmallow.validate import OneOf

from .constant import METHODS


class WhenConfigSchema(Schema):
    path = fields.String(required=True)
    method = fields.String(default='GET', validate=OneOf(METHODS))
    type = fields.String(default='application/json', validate=OneOf(['application/json']))
    header = fields.Dict()
    body = fields.Dict()
    query = fields.Dict()


class ThenConfigSchema(Schema):
    method = fields.String(default='GET', validate=OneOf(METHODS))
    type = fields.String(default='application/json', validate=OneOf(['application/json']))
    header = fields.Dict()
    body = fields.Raw()
    code = fields.Int(default=HTTPStatus.OK, validate=OneOf(list(map(int, HTTPStatus))))


class ConfigSchema(Schema):
    id = fields.String(required=True)
    description = fields.String()
    when = fields.Nested(WhenConfigSchema, required=False)
    then = fields.Nested(ThenConfigSchema, required=False)
