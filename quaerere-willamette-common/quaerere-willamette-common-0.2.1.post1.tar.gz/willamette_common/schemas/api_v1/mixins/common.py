from marshmallow import fields, Schema


class SourceAccounting(Schema):
    data_origin = fields.String(required=True)
    datetime_acquired = fields.DateTime()
