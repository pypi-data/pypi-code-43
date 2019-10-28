__all__ = ['WebPageFieldsMixin']

from marshmallow import fields

from .common import SourceAccounting


class WebPageFieldsMixin:
    source_accounting = fields.Nested(SourceAccounting, required=True)
    text = fields.String(required=True)
    url = fields.Url(required=True)
    web_site_key = fields.String(required=True)
