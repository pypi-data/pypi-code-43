from marshmallow import fields


class SourceAccounting:
    data_origin = fields.String(required=True)
    datetime_acquired = fields.DateTime()
