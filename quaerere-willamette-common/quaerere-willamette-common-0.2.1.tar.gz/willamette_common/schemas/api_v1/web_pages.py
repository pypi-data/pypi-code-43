__all__ = ['WebPageSchema']

from marshmallow import fields
from quaerere_base_common.schema import BaseSchema

from .mixins import WebPageFieldsMixin


class WebPageSchema(WebPageFieldsMixin, BaseSchema):
    _key = fields.String()
