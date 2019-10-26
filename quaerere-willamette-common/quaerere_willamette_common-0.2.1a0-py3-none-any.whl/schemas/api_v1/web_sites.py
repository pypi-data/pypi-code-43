__all__ = ['WebSiteSchema']

from marshmallow import fields
from quaerere_base_common.schema import BaseSchema

from .mixins import WebSiteFieldsMixin


class WebSiteSchema(WebSiteFieldsMixin, BaseSchema):
    _key = fields.String()
