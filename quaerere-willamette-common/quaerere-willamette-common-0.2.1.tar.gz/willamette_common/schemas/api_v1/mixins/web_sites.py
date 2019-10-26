__all__ = ['WebSiteFieldsMixin']

from marshmallow import fields

from .common import SourceAccounting


class WebSiteFieldsMixin:
    inLanguage = fields.String(allow_none=True)
    source_accounting = fields.Nested(SourceAccounting, required=True)
    url = fields.Url(required=True)
