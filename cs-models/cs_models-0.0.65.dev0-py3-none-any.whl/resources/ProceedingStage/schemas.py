from marshmallow import (
    Schema,
    fields,
    validate,
)


class ProceedingStageResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    ptab2_proceeding_id = fields.Integer(required=True)
    stage = fields.String(required=True, validate=not_blank)
    is_active = fields.Boolean(required=True)
    filed_date = fields.DateTime(allow_none=True)
    due_date = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)
